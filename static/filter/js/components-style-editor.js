
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
                'default': this.itemStyle
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


Vue.component('style-editor-ui', {
    template: '\
        <div class="style-editor-ui"> \
            <h3>Edit Style</h3> \
            <div class="style-editor-ui-main"> \
                <style-editor-fontsize :value="fontsize" @input="setFontSize"></style-editor-fontsize> \
            </div> \
        </div>',

    props: ['styleData'],

    data: function() { return {
        fontsize: this.styleData.fontsize || null,
    }},

    methods: {
        buildStyle: function() {
            var style = {};
            if (this.fontsize) {
                this.$set(style, 'fontsize', this.fontsize);
            }
            this.$emit('input', style);
        },
        setFontSize: function (value) {
            console.log("setFontSize", value)
            this.fontsize = value;
            this.buildStyle();
        }
    },

    watch: {
        styleData: function (newValue, oldValue) {
            console.log("Fontsize -> ", newValue.fontsize);
            this.fontsize = newValue.fontsize;
        }
    },
})


Vue.component('style-editor-fontsize', {
    template: '\
        <p class="fontsize"> \
            <input type="checkbox" v-model="hasFontSize"> \
            <label for="style-editor-fontsize">Font Size:</label> \
            <select \
                id="style-editor-fontsize" \
                v-bind:value="value" \
                v-on:input="$emit(\'input\', $event.target.value)"> \
                <option v-for="x in allowedFontSizes">{{ x }}</option> \
            </select> \
        </p>',

    props: ['value'],

    computed: {
        hasFontSize: {
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
