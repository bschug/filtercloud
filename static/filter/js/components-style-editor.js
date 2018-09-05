
Vue.component('style-editor', {
    template: '\
        <div class="style-editor"> \
            <h2>{{ title }}<span class="tooltip"><slot></slot></span></h2> \
            <p> \
                <span v-for="item in items" @click="onClickItem(item)" v-bind:class="{ selected: editorOpenFor === item.style }"> \
                    <itempreview \
                        :item="item.name" \
                        :item-style="item.style" \
                        :item-rarity="item.rarity" \
                        :item-class="item.itemClass" \
                        :deletable="false" \
                        :hidden="false"> \
                    </itempreview> \
                </span> \
            </p> \
            <style-editor-ui v-if="isEditorOpen" :style-data="editedStyleData" @input="saveStyle"></style-editor-ui> \
        </div>',

    props: ['title', 'itemStyle', 'variants'],

    data: function() { return {
        editorOpenFor: null
    }},

    computed: {
        isEditorOpen: function() {
            return this.editorOpenFor !== null;
        },

        editedStyleData: function() {
            if (this.editorOpenFor === null) {
                return null;
            }
            var parts = this.editorOpenFor.split('.');
            var category = parts[0];
            var variant = parts[1];

            return Style.data[category][variant] || {};
        },

        items: function() {
            var variants = ['default'];
            if (this.variants.trim().length > 0) {
                variants = variants.concat( this.variants.trim().split(',') );
            }

            var nameOverrides = {
                'breach': 'League Item',
                'divcard': 'Divination Card'
            };
            var styleOverrides = {
            };
            var rarityOverrides = {
                'magic': 'magic',
                'rare': 'rare',
                'unique': 'unique'
            }
            var iclassOverrides = {
                'currency': 'Stackable Currency',
                'gem': 'Active Skill Gems',
                'divcard': 'Divination Cards',
                'quest': 'Quest Items'
            }
            if (this.itemStyle === 'map') {
                iclassOverrides = new Proxy({}, {
                    get: (target, name) => 'Maps'
                })
            }

            var self = this;
            var result = variants.map(function (v) { return {
                name: nameOverrides[v] || StrUtils.capitalize(v),
                style: styleOverrides[v] || (self.itemStyle + '.' + v),
                rarity: rarityOverrides[v] || 'normal',
                itemClass: iclassOverrides[v] || 'Wands'
            }});
            return result;
        }
    },

    methods: {
        onClickItem: function (item) {
            if (this.editorOpenFor === item.style) {
                this.editorOpenFor = null;
            } else {
                this.editorOpenFor = item.style;
            }
        },
        saveStyle: function (styleData) {
            // Get full style identifier (including the optional .default)
            // split into its separate parts
            var parts = this.editorOpenFor.split('.');
            if (parts.length == 1) {
                parts.push('default');
            }
            var category = parts[0];
            var variant = parts[1];

            this.$set(Style.data[category], variant, styleData);
        }
    }
})

/*
 * This one is a bit more complicated:
 * We hold a copy of the style definition as an internal state.
 * Whenever the external state changes, we overwrite out internal state with it.
 * Whenever one of the properties is changed, we write it to the internal state and
 * then emit that one to the parent.
 */
Vue.component('style-editor-ui', {
    template: '\
        <div class="style-editor-ui"> \
            <h3>Edit Style</h3> \
            <div class="style-editor-ui-main"> \
                <style-editor-fontsize :value="fontsize" @input="fontsize = $event">Font Size</style-editor-fontsize> \
                <style-editor-color :value="textcolor" @input="textcolor = $event" id="textcolor">Text Color</style-editor-color> \
                <style-editor-color :value="background" @input="background = $event" id="background">Background</style-editor-color> \
                <style-editor-color :value="border" @input="border = $event" id="border">Border Color</style-editor-color> \
                <style-editor-mapicon :value="map_icon" @input="map_icon = $event">Minimap Icon</style-editor-mapicon> \
            </div> \
        </div>',

    props: ['styleData'],

    data: function() { return {
        state: this.styleData
    }},

    computed: {
        fontsize: {
            get() { return this.state.fontsize },
            set(newValue) { this.state.fontsize = newValue; this.emitStyle(); }
        },
        textcolor: {
            get() { return this.state.textcolor },
            set(newValue) { this.state.textcolor = newValue; this.emitStyle(); }
        },
        background: {
            get() { return this.state.background },
            set(newValue) { this.state.background = newValue; this.emitStyle(); }
        },
        border: {
            get() { return this.state.border },
            set(newValue) { this.state.border = newValue; this.emitStyle(); }
        },
        map_icon: {
            get() { return this.state.map_icon },
            set(newValue) { Vue.set(this.state, 'map_icon', newValue); this.emitStyle(); }
        }
    },

    methods: {
        emitStyle: function() {
            var style = {};
            for (var key of Object.keys(this.state)) {
                if (key[0] !== '$') {
                    style[key] = this.state[key];
                }
            }
            this.$emit('input', style);
        },
    },

    watch: {
        styleData: function (newValue, oldValue) {
            this.state = newValue;
        }
    },
})


Vue.component('style-editor-fontsize', {
    template: '\
        <p class="fontsize"> \
            <input type="checkbox" v-model="hasValue"> \
            <label for="style-editor-fontsize"><slot></slot>:</label> \
            <select \
                id="style-editor-fontsize" \
                v-bind:value="value" \
                v-on:input="$emit(\'input\', $event.target.value)"> \
                <option v-for="x in allowedFontSizes">{{ x }}</option> \
            </select> \
        </p>',

    props: ['value'],

    computed: {
        hasValue: {
            get() {
                return !!this.value;
            },
            set(newValue) {
                if (!newValue) { this.$emit('input', null); }
            }
        },
        allowedFontSizes: function() {
            var result = [];
            for (var i=18; i <= 45; i++) {
                result.push(i);
            }
            return result;
        }
    }
})


Vue.component('style-editor-color', {
    template: '\
        <p class="color"> \
            <input type="checkbox" v-model="hasValue"> \
            <label :for="\'style-editor-\' + id"><slot></slot>:</label> \
            <input type="color" :value="hexcolor" @input="hexcolor = $event.target.value"> \
            <input type="range" min="0" max="255" :value="alpha" @input="alpha = $event.target.value"> \
        </p>',

    props: ['value', 'id'],

    computed: {
        hasValue: {
            get() {
                return !!this.value;
            },
            set(newValue) {
                if (!newValue) { this.$emit('input', null); }
            }
        },
        hexcolor: {
            get() {
                if (!this.value) {
                    return '#FFFFFF';
                }
                var rgba = this.value.split(' ');
                var r = parseInt(rgba[0]);
                var g = parseInt(rgba[1]);
                var b = parseInt(rgba[2]);

                var hexR = (r < 16 ? '0' : '') + r.toString(16).toLowerCase();
                var hexG = (g < 16 ? '0' : '') + g.toString(16).toLowerCase();
                var hexB = (b < 16 ? '0' : '') + b.toString(16).toLowerCase();

                return '#' + hexR + hexG + hexB;
            },
            set(newValue) {
                var r = parseInt(newValue.substring(1,3), 16);
                var g = parseInt(newValue.substring(3,5), 16);
                var b = parseInt(newValue.substring(5,7), 16);
                var a = this.alpha;
                if (a < 255) {
                    this.$emit('input', r + ' ' + g + ' ' + b + ' ' + a);
                } else {
                    this.$emit('input', r + ' ' + g + ' ' + b);
                }
            }
        },
        alpha: {
            get() {
                if (!this.value) {
                    return 255;
                }
                var rgba = this.value.split(' ');
                if (rgba.length < 4) {
                    return 255;
                }
                return parseInt(rgba[3]);
            },
            set(newValue) {
                var old = this.value ? this.value.split(' ') : [0,0,0];
                this.$emit('input', old[0] + ' ' + old[1] + ' ' + old[2] + ' ' + newValue);
            }
        }
    }
})


Vue.component('style-editor-mapicon', {
    template: '\
        <div class="mapicon"> \
            <span><slot></slot>:<span class="tooltip">Map icons are currently not shown in the preview. They still propagate from the defaults like all other settings.</span></span> \
            <p> \
                <input type="checkbox" v-model="hasShape"> \
                <label for="style-editor-mapicon-shape">Shape:</label> \
                <select :value="size" @input="size = $event.target.value" id="style-editor-mapicon-shape"> \
                    <option value="0">Large</option> \
                    <option value="1">Medium</option> \
                    <option value="2">Small</option> \
                </select> \
            </p> \
            <p> \
                <input type="checkbox" v-model="hasColor">\
                <select class="color-constant" :value="color" @input="color = $event.target.value">\
                    <option value="Red">Red</option>\
                    <option value="Green">Green</option>\
                    <option value="Blue">Blue</option>\
                    <option value="Brown">Brown</option>\
                    <option value="White">White</option>\
                    <option value="Yellow">Yellow</option>\
                </select>\
            </p> \
            <p> \
                <input type="checkbox" v-model="hasShape">\
                <select class="mapicon" id="style-editor-mapicon" :value="shape" @input="shape = $event.target.value">\
                    <option value="Circle">Circle</option>\
                    <option value="Square">Square</option>\
                    <option value="Triangle">Triangle</option>\
                    <option value="Hexagon">Hexagon</option>\
                    <option value="Diamond">Diamond</option>\
                    <option value="Star">Star</option>\
                </select>\
            </p> \
        </div>',

    props: ['value'],

    data: function() { return {
        state: this.value || {}
    }},

    watch: {
        value: function(newValue) { console.log("NEW", newValue); this.state = newValue || {}; }
    },

    computed: {
        hasShape: {
            get() { return !!this.state.shape },
            set(newValue) {
                if (!newValue) {
                    Vue.delete(this.state, 'shape');
                    this.$emit('input', this.state);
                }
            }
        },
        shape: {
            get() { return this.state.shape },
            set(newValue) {
                Vue.set(this.state, 'shape', newValue);
                this.$emit('input', this.state);
            }
        },
        hasColor: {
            get() { return !!this.state.color },
            set(newValue) {
                if (!newValue) {
                    Vue.delete(this.state, 'color');
                    this.$emit('input', this.state);
                }
            }
        },
        color: {
            get() { return this.state.color },
            set(newValue) {
                Vue.set(this.state, 'color', newValue);
                this.$emit('input', this.state);
            }
        },
        hasSize: {
            get() { return !!this.state.size },
            set(newValue) {
                if (!newValue) {
                    Vue.delete(this.state, 'size');
                    this.$emit('input', this.state);
                }
            }
        },
        size: {
            get() { return this.state.size },
            set(newValue) {
                Vue.set(this.state, 'size', parseInt(newValue));
                this.$emit('input', this.state);
            }
        }
    }
})