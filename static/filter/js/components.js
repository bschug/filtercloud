Vue.component('checkboxwithtooltip', {
    template: '\
        <p>\
            <input type="checkbox" \
                :id="id" \
                :checked="value" \
                @change="e => updateValue(e.target.checked)"> \
            <label :for="id">{{ label }}</label>  \
            <span class="tooltip"> \
                <slot></slot> \
            </span> \
        </p>',
    props: ['value', 'id', 'label'],
    methods: {
        updateValue: function(value) {
            ga('send', 'event', 'configure', this.id);
            this.$emit('input', value);
        }
    }
});


Vue.component('textboxwithtooltip', {
    template: '\
        <p>\
            <label :for="id">{{ label }}</label> \
            <input type="text" :placeholder="placeholder" :id="id" \
                   v-model="value" @change="e => updateValue(e.target.value)">\
            <span class="tooltip"> \
                <slot></slot> \
            </span> \
        </p>',
    props: ['value', 'id', 'label', 'placeholder'],
    methods: {
        updateValue: function(value) {
            ga('send', 'event', 'configure', this.id);
            this.$emit('input', value);
        }
    }
});


Vue.component('dropdownwithtooltip', {
    template: '\
        <p>\
            <label :for="id">{{ label }}</label>\
            <select v-model="selectedLabel"> \
                <option v-for="label in optionLabels">{{ label }}</option> \
            </select> \
            <span class="tooltip"> \
                <slot></slot> \
            </span>\
        </p>',
    props: ['label', 'options', 'optionLabels', 'value', 'id'],
    data: function() {
        return {
            selectedOption: this.value
        }
    },
    computed: {
        selectedLabel: {
            get: function() {
                var idx = this.options.indexOf(this.selectedOption);
                return this.optionLabels[idx];
            },
            set: function(newValue) {
                ga('send', 'event', 'configure', this.id);
                var idx = this.optionLabels.indexOf(newValue);
                this.selectedOption = this.options[idx];
                this.$emit('input', this.options[idx]);
            }
        }
    }
});


Vue.component('sidebarlink', {
    template: '<p class="link" \
        :class="{ selected: currentPage === page }" \
        @click="setPage(page)">{{ page }}</p>',
    props:['page', 'currentPage'],
    methods: {
        setPage: function(page) {
            ga('set', 'page', '/#/' + page);
            ga('send', 'pageview');
            this.$emit('update:currentPage', page);
        }
    }
});


Vue.component('itemlist', {
    template: '\
        <div class="item-list bordered-section">\
            <select class="item-class-filter" v-model="itemClassFilter">\
                <option v-for="itemClass in allowedItemClasses">{{ itemClass }}</option>\
            </select>\
            <h2>{{ title }}<span class="tooltip"><slot></slot></span></h2>\
            <div class="item-list-inner">\
                <itempreview \
                    v-for="item in filteredItems" :key="item" \
                    :item="item" :item-style="itemStyle" :item-rarity="itemRarity" :item-class="getItemClass(item)" \
                    :deletable="true" @deleted="deleteItem(item)"/>\
            </div>\
            <input v-if="!readOnly" type="text" v-model="itemInputName" @keydown.enter="addItem(itemInputName); itemInputName=\'\'">\
            <button v-if="!readOnly" type="button" @click="addItem(itemInputName); itemInputName=\'\'">Add</button>\
        </div>',
    props: ['id', 'title', 'items', 'itemStyle', 'itemRarity', 'itemClass', 'readOnly'],
    data: function() { return {
        itemInputName: '',
        itemClassFilter: 'All'
    }},
    computed: {
        filteredItems: function() {
            var self = this;
            if (self.itemClassFilter === 'All') {
                return self.items;
            }
            return self.items.filter(function(item) {
                return self.itemClassFilter === GameData.getItemClass(item);
            });
        },
        allowedItemClasses: function() {
            return ['All']
                .concat(_.sortBy(GameData.itemCategories['weapons']))
                .concat(_.sortBy(GameData.itemCategories['armour']))
                .concat(_.sortBy(GameData.itemCategories['jewelry']))
                .filter(this.containsItemOfClass)
        }
    },
    methods: {
        deleteItem: function(item) {
            this.$emit('update:items', this.items.filter(function(x) { return x !== item; }));
            ga('send', 'event', 'configure', this.id + '-remove');
        },
        addItem: function(item) {
            this.items.push(item);
            ga('send', 'event', 'configure', this.id + '-add');
        },
        containsItemOfClass: function(itemClass) {
            if (itemClass === 'All') {
                return true;
            }
            if (!this.items) {
                // this happens during initialization -- it tries to get allowedItemClasses before the props are
                // part of the namespace, so this would fail and break everything
                return true;
            }
            var ic = GameData.itemClasses[itemClass];
            for (var i=0; i < this.items.length; i++) {
                if (this.items[i] in ic) {
                    return true;
                }
            }
            return false;
        },
        getItemClass: function(item) {
            return GameData.getItemClass(item);
        }
    }
});


Vue.component('itemclasslist', {
    template: '\
        <div class="item-list bordered-section">\
            <h2>{{ title }}</h2>\
            <p class="explanation"><slot></slot></p>\
            <div class="item-list-inner">\
                <itempreview \
                    v-for="item in items" :key="item" \
                    :item="item" :item-style="itemStyle" :item-rarity="itemRarity" :item-class="item" \
                    :deletable="true" @deleted="deleteItem(item)"/>\
            </div>\
            <p>\
                <select v-model="selectedAddItem">\
                    <option disabled value="">Add</option>\
                    <option v-for="itemClass in itemClasses">{{ itemClass }}</option>\
                </select>\
                <span class="tooltip">Add an item class to the list.</span>\
            </p>\
        </div>',
    props: ['id', 'title', 'category', 'items', 'itemStyle', 'itemRarity'],
    data: function() { return {
        selectedAddItem: ''
    }},
    computed: {
        itemClasses: function() { return GameData.itemCategories[this.category]; }
    },
    methods: {
        deleteItem: function(item) {
            this.$emit('update:items', this.items.filter(function(x) { return x !== item; }));
            ga('send', 'event', 'configure', this.id + '-remove');
        },
        addItem: function(item) {
            if (item === "") {
                return;
            }
            this.items.push(item);
            ga('send', 'event', 'configure', this.id + '-add');
        }
    },
    watch: {
        'selectedAddItem': function(val) {
            if (val !== '') {
                this.addItem(val);
                this.selectedAddItem = '';
            }
        }
    }
});


Vue.component('itempreview', {
    template: '\
        <span class="item-preview" :style="style">\
            {{ item }}\
            <mapicon v-if="hasMapIcon" :value="mapIcon"></mapicon> \
            <img src="images/buttons/close.png" alt="delete" v-if="deletable" class="delete-button" @click="deleteItem"></img>\
        </span>',

    props: ['item', 'itemStyle', 'deletable', 'itemRarity', 'itemClass', 'hidden'],

    computed: {
        styleData: function() {
            return Style.getEffectiveStyle(FilterCloud.app.style, this.itemStyle, this.itemRarity, this.itemClass);
        },
        style: function() {
            return Style.toCSS(this.styleData, this.hidden);
        },
        hasMapIcon: function() {
            return !!this.mapIcon;
        },
        mapIcon: function() {
            return this.styleData.map_icon;
        },
    },

    methods: {
        deleteItem: function() { this.$emit('deleted'); }
    }
});


Vue.component('mapicon', {
    template: '\
        <svg xmlns="http://www.w3.org/2000/svg" \
            :width="size" :height="size" viewBox="0 0 1 1" class="map-icon"> \
            <circle v-if="shape == \'Circle\'" \
                cx="0.5" \
                cy="0.5" \
                r="0.35" \
                :style="\'stroke:black; stroke-width:0.075; fill:\' + svgColor"> \
            </circle> \
            <polygon v-if="shape == \'Square\'" \
                points="0.15,0.15 0.15,0.85 0.85,0.85 0.85,0.15" \
                :style="\'stroke:black; stroke-width:0.075; fill:\' + svgColor"> \
            </polygon> \
            <g v-if="shape == \'Triangle\'"> \
                <polygon \
                    points="0.1,0.9 0.5,0.1 0.9,0.9" \
                    :style="\'stroke:black; stroke-width:0.075; fill:\' + svgColor"> \
                </polygon> \
                <line x1="0.27" y1="0.55" x2="0.73" y2="0.55" \
                    style="stroke:black; stroke-width:0.04"> \
                </line> \
            </g> \
            <polygon v-if="shape == \'Hexagon\'" \
                points="0.5,0.08 0.14,0.29 0.14,0.71 0.5,0.92 0.86,0.71 0.86,0.29" \
                :style="\'stroke:black; stroke-width:0.075; fill:\' + svgColor"> \
            </polygon> \
            <polygon v-if="shape == \'Star\'" \
                points="0.5,0.12 0.4,0.42 0.09,0.42 0.34,0.6 0.24,0.9 0.5,0.72 0.75,0.9 0.66,0.6 0.91,0.42 0.6,0.42" \
                :style="\'stroke:black; stroke-width:0.075; fill:\' + svgColor"> \
            </polygon> \
            <g v-if="shape == \'Diamond\'"> \
                <polygon \
                    points="0.5,0.96 0.27,0.73 0.5,0.5 0.73,0.73" \
                    :style="\'stroke:black; stroke-width:0.075; fill:\' + svgColor"> \
                </polygon> \
                <polygon \
                    points="0.5,0.5 0.27,0.27 0.5,0.04 0.73,0.27" \
                    :style="\'stroke:black; stroke-width:0.075; fill:\' + svgColor"> \
                </polygon> \
                <polygon \
                    points="0.42,0.5 0.24,0.69 0.04,0.5 0.23,0.31" \
                    :style="\'stroke:black; stroke-width:0.06; fill:\' + svgColor"> \
                </polygon> \
                <polygon \
                    points="0.58,0.5 0.77,0.31 0.96,0.5 0.77,0.69" \
                    :style="\'stroke:black; stroke-width:0.06; fill:\' + svgColor"> \
                </polygon> \
            </g> \
        </svg>',

    props: ['value'],

    computed: {
        size: function() {
            return 10 + 10 * (2 - this.value.size);
        },
        shape: function() {
            return this.value.shape;
        },
        svgColor: function() {
            var c = Style.colorNameToCSS( this.value.color );
            return 'rgb(' + c.r + ',' + c.g + ',' + c.b + ')'
        }
    }
})



Vue.component('thresholdslider', {
    template: '\
        <div class="threshold-slider"> \
            <h3>{{ title }}<span class="tooltip"><slot></slot></span></h3> \
            <span class="value"><span class="math">{{ op }}</span> {{ formattedValue }}</span> \
            <img src="images/items/currency/chaos.png"></img> \
            <input type="range" min="-3001" max="3000" v-model="sliderPosition" class="slider"> \
            <button class="openclose" :class="isExpanded ? \'less\' : \'more\'" @click="toggleExpand"/> \
            <p v-show="isExpanded"> \
                <itempreview v-for="item in overrides" :key="item" \
                    :item="item" :item-style="itemStyle" :deletable="true" \
                    :item-rarity="itemRarity" :item-class="itemClass" :hidden="hidden" \
                    @deleted="deleteOverride(item)"> \
                </itempreview> \
                <select v-model="selectedOverride"> \
                    <option disabled value="">Add Override</option> \
                    <option v-for="item in allItems">{{ item }}</option> \
                </select> \
            </p> \
        </div> \
        ',
    props: ['id', 'value', 'title', 'op', 'overrides', 'prices', 'itemStyle', 'itemRarity', 'itemClass', 'hidden'],
    data: function() { return {
        'sliderPosition': this.value === 0 ? -3001 : Math.log10(MathUtils.clamp(this.value, 0.001, 1000)) * 1000,
        'isExpanded': this.overrides && (this.overrides.length > 0),
        'selectedOverride': '',
        'allItems': Object.keys(this.prices).sort(),
        'lastUpdate': new Date()
    };},
    computed: {
        formattedValue: function() {
            if (this.value > 10) {
                return Math.round(this.value);
            } else if (this.value >= 1) {
                return this.value.toFixed(1);
            } else if (this.value >= 0.1) {
                return this.value.toFixed(2);
            } else {
                return this.value.toFixed(3);
            }
        },
        hasJustMoved: function() {
            var now = new Date();
            return now.getTime() - this.lastUpdate.getTime() < 1000;
        }
    },
    watch: {
        'sliderPosition': function(val) {
            if (!this.hasJustMoved) {
                ga('send', 'event', 'configure', this.id + '-threshold');
            }
            this.$emit('input', val < -3000 ? 0 : Math.pow(10, val / 1000));
        },
        'selectedOverride': function(val) {
            if (val !== '') {
                this.addOverride(val);
                this.selectedOverride = '';
            }
        }
    },
    methods: {
        'toggleExpand': function() {
            ga('send', 'event', 'configure', this.id + '-override-toggle');
            this.isExpanded = !this.isExpanded;
        },
        'deleteOverride': function(item) {
            ga('send', 'event', 'configure', this.id + '-override-remove');
            this.$emit('update:overrides', this.overrides.filter(function(x) { return x !== item; }));
        },
        'addOverride': function(item) {
            ga('send', 'event', 'configure', this.id + '-override-add');
            this.$emit('update:overrides', this.overrides.concat([item]));
        }
    }
});


Vue.component('linearslider', {
    template: '\
        <div class="threshold-slider"> \
            <h3>{{ title }}<span class="tooltip"><slot></slot></span></h3> \
            <span class="value"><span class="math">{{ op }}</span> {{ value }}</span> \
            <input type="range" :min="minValue" :max="maxValue" v-model="sliderPosition" class="slider"> \
        </div> \
        ',
    props: ['id', 'value', 'title', 'minValue', 'maxValue', 'op'],
    data: function() { return {
        'sliderPosition': this.value,
        'lastUpdate': new Date()
    };},
    computed: {
        // This tells us if the slider has been moved in the last second. We don't generate an analytics event in that
        // case. Otherwise it would spam events while the user is moving the slider.
        hasJustMoved: function() {
            var now = new Date();
            return now.getTime() - this.lastUpdate.getTime() < 1000;
        }
    },
    watch: {
        'sliderPosition': function(val) {
            if (!this.hasJustMoved) {
                ga('send', 'event', 'configure', this.id);
            }
            this.lastUpdate = new Date();
            this.$emit('input', parseInt(val));
        },
    },
});


Vue.component('thresholditemlist', {
    template: '\
        <div class="item-list bordered-section">\
            <h2>Preview<span class="tooltip"><slot></slot></span></h2>\
            <div class="item-list-inner">\
                <itempreview \
                    v-for="item in itemList" :key="item" \
                    :item="item" :item-style="getStyleForItem(item)" :item-rarity="itemRarity" :item-class="getItemClass(item)" \
                    :deletable="false" :hidden="isHidden[item]"/>\
            </div>\
        </div>',

    props: [
        'prices', 'thresholds', 'styleContext', 'hideWorthless',
        'overrides', 'styleOverrides', 'itemRarity'],

    computed: {
        itemList: function() {
            var self = this;
            return _.sortBy(Object.keys(self.prices), [function(x) { return -self.prices[x] }]);
        },
        isHidden: function() {
            result = {};
            for (var item in this.prices) {
                var tier = this.getItemTier(item);
                result[item] = (tier === 'hidden');
            }
            return result;
        },

        // Override list is stored as Tier -> [Item] to make UI easier to implement.
        // We need Item -> Tier here.
        tierOverrides: function() {
            var result = {};
            for (var tier in this.overrides) {
                for (var i=0; i < this.overrides[tier].length; i++) {
                    var item = this.overrides[tier][i];
                    result[item] = tier;
                }
            }
            return result;
        }
    },

    methods: {
        getStyleForItem: function(item) {
            if (this.styleOverrides[item]) {
                return this.styleOverrides[item];
            }
            var tier = this.getItemTier(item);
            var styleName = this.getStyleNameForTier(tier);
            return styleName + '.' + this.styleContext;
        },

        getItemTier: function(item) {
            if (this.tierOverrides[item]) {
                return this.tierOverrides[item];
            }
            var price = this.prices[item];
            if (price >= this.thresholds.top_tier) {
                return 'top_tier';
            } else if (price >= this.thresholds.valuable) {
                return 'valuable';
            } else if (price >= this.thresholds.worthless) {
                return 'mediocre';
            } else if (price >= this.thresholds.hidden) {
                return 'worthless';
            } else {
                return 'hidden';
            }
        },

        getItemClass: function(item) {
            return GameData.getItemClass(item);
        },

        getStyleNameForTier: function(tier) {
            return {
                top_tier: 'strong_highlight',
                valuable: 'highlight',
                mediocre: 'normal',
                worthless: 'smaller',
                hidden: 'smaller'
            }[tier];
        }
    }
});


Vue.component('socketlist', {
    template: '\
        <div class="bordered-section">\
            <p class="socket-list" v-for="entry in socketConfigs">\
                <socketconfig :config="entry" @deleted="deleteSocketConfig(entry)"></socketConfig>\
            </p>\
            <p><button class="addbutton" @click="addSocketConfig">Add</button></p>\
        </div>',
    props: ['socketConfigs'],
    methods: {
        addSocketConfig: function() {
            this.socketConfigs.push({'sockets':'', 'level': 0});
            this.$emit('input', this.socketConfigs);
            ga('send', 'event', 'configure', 'sockets-add');
        },
        deleteSocketConfig: function(cfg) {
            var idx = this.socketConfigs.indexOf(cfg);
            this.socketConfigs.splice(idx, 1);
            this.$emit('input', this.socketConfigs);
            ga('send', 'event', 'configure', 'sockets-remove');
        }
    }
});


Vue.component('socketconfig', {
    template: '\
        <p class="socket-config">\
            <label>Sockets:</label><input type="text" v-model="config.sockets"></input>\
            <label>Level:</label><input type="number" v-model.number="config.level"></input>\
            <img src="images/buttons/close.png" alt="delete" class="delete-button" @click="deleteItem"></img>\
        </p>',
    props: ['config'],
    methods: {
        deleteItem: function() {
            this.$emit('deleted', null);
        }
    }
});


Vue.component('craftingconfig', {
    template: '\
        <div class="bordered-section">\
            <h2>{{ title }}<span class="tooltip"><slot></slot></span></h2>\
            <checkboxwithtooltip v-if="\'show\' in value" :id="id + \'-show\'" v-model="value.show" label="Show">\
                Completely enable / disable this rule.\
            </checkboxwithtooltip>\
            <p v-if="\'ilvl\' in value"><label :for="id + \'ilvl\'">Item Level</label>\
                <input :id="id + \'ilvl\'" type="number" v-model.number="value.ilvl" @input="ilvl_changed()"></input>\
                <span class="tooltip">Show only items with at least this item level. Set to 0 to ignore.</span>\
            </p>\
            <p v-if="\'links\' in value"><label :for="id + \'links\'">Linked Sockets</label>\
                <input type="number" v-model.number="value.links" @input="links_changed"></input>\
                <span class="tooltip">Show only items with at least this many linked sockets. Set to 0 to ignore.</span>\
            </p>\
            <dropdownwithtooltip :id="id + \'-highlight\'" v-model="value.highlight" label="Highlight"\
                :options="[\'strong\', true, false]" :option-labels="[\'Strong\', \'Regular\', \'None\']">\
                Use highlighting style for these items.\
            </dropdownwithtooltip>\
            <itemlist v-if="\'basetypes\' in value" :id="id + \'-basetypes\'" title="Base Types" :items="value.basetypes"\
                      :itemStyle="value.highlight ? \'highlight.normal\' : \'normal.normal\'" itemRarity="normal" itemClass="?">\
                Base types that his rule should apply for.\
            </itemlist>\
        </div>',
    props: ['id', 'title', 'value'],
    methods: {
        // analytics hooks for the parts that aren't tracked by subcomponents already
        'ilvl_changed': function() { ga('send', 'event', 'configure', this.id + '-ilvl'); },
        'links_changed': function() { ga('send', 'event', 'configure', this.id + '-links'); }
    }
});



Vue.component('leagueuniqueselection', {
    template: '\
        <div class="league-unique-selection"> \
            <h3>{{ title }}<span class="tooltip"><slot></slot></span></h3> \
            <ul> \
                <span v-for="league in allLeagues"> \
                    <input type="checkbox" :id="id + \'-\' + league" :value="league" v-model="checkedLeagues"> \
                    <label :for="id + \'-\' + league">{{ league }}</label> \
                </span> \
            </ul> \
        </div>',
    props: ['id', 'value', 'allLeagues', 'title'],
    data: function() { return {
        'checkedLeagues': this.value
    }},
    watch: {
        'checkedLeagues': function(val) {
            this.$emit('input', val);
        }
    }
});
