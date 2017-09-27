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
        updateValue: function(value) { this.$emit('input', value); }
    }
});


Vue.component('sidebarlink', {
    template: '<p class="link" \
        :class="{ selected: currentPage === page }" \
        @click="setPage(page)">{{ page }}</p>',
    props:['page', 'currentPage'],
    methods: {
        setPage: function(page) { this.$emit('update:currentPage', page); }
    }
});


Vue.component('itemlist', {
    template: '\
        <div class="item-list">\
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
    props: ['title', 'items', 'itemStyle', 'itemRarity', 'itemClass', 'readOnly'],
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
        },
        addItem: function(item) {
            this.items.push(item);
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
                if (ic.indexOf(this.items[i]) >= 0) {
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


Vue.component('itempreview', {
    template: '\
        <span class="item-preview" :style="style">\
            {{ item }}\
            <img src="images/close_button.png" alt="delete" v-if="deletable" class="delete-button" @click="deleteItem"></img>\
        </span>',

    props: ['item', 'itemStyle', 'deletable', 'itemRarity', 'itemClass', 'hidden'],

    computed: {
        style: function() {
            return Style.toCSS(Style.getEffectiveStyle(Style.data, this.itemStyle, this.itemRarity, this.itemClass), this.hidden);
        }
    },

    methods: {
        deleteItem: function() { this.$emit('deleted'); }
    }
});


Vue.component('thresholdslider', {
    template: '\
        <div class="threshold-slider"> \
            <h3>{{ title }}</h3> \
            <span class="value">{{ formattedValue }}</span> \
            <img src="images/items/currency/chaos.png"></img> \
            <input type="range" min="-3001" max="3000" v-model="sliderPosition" class="slider"> \
        </div> \
        ',
    props: ['value', 'title'],
    data: function() { return {
        'sliderPosition': this.value === 0 ? -3001 : Math.log10(MathUtils.clamp(this.value, 0.001, 1000)) * 1000
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
        }
    },
    watch: {
        'sliderPosition': function(val) {
            this.$emit('input', val < -3000 ? 0 : Math.pow(10, val / 1000));
        },
    },
});


Vue.component('linearslider', {
    template: '\
        <div class="threshold-slider"> \
            <h3>{{ title }}</h3> \
            <span class="value">{{ value }}</span> \
            <input type="range" :min="minValue" :max="maxValue" v-model="sliderPosition" class="slider"> \
        </div> \
        ',
    props: ['value', 'title', 'minValue', 'maxValue'],
    data: function() { return {
        'sliderPosition': this.value
    };},
    watch: {
        'sliderPosition': function(val) {
            this.$emit('input', val);
        },
    },
});


Vue.component('thresholditemlist', {
    template: '\
        <div class="item-list">\
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
        'tierOverrides', 'styleOverrides', 'hideOverrides',
        'itemRarity'],

    computed: {
        itemList: function() {
            var self = this;
            return _.sortBy(Object.keys(self.prices), [function(x) { return -self.prices[x] }]);
        },
        isHidden: function() {
            result = {};
            for (var item in this.prices) {
                if (ArrayUtils.contains(this.hideOverrides, item)) {
                    return true;
                }
                var tier = this.getItemTier(item);
                result[item] = (tier === 'hidden');
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

