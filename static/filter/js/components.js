Vue.component('checkboxwithtooltip', {
    template: '\
        <span> \
            <input type="checkbox" \
                :id="id" \
                :value="value" \
                @input="updateValue($event.target.value)"> \
            <label :for="id">{{ label }} \
                <span class="tooltip"> \
                    <slot></slot> \
                </span> \
            </label> \
        </span>',
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
            <h2>{{ title }}<span class="tooltip"><slot></slot></span></h2>\
            <div class="item-list-inner">\
                <itempreview \
                    v-for="item in filteredItems" :key="item" \
                    :item="item" :item-style="itemStyle" :item-rarity="itemRarity" :item-class="getItemClass(item)" \
                    :deletable="true" @deleted="deleteItem(item)"/>\
            </div>\
            <input v-if="!readOnly" type="text" v-model="itemInputName" @keydown.enter="addItem(itemInputName); itemInputName=\'\'">\
            <button v-if="!readOnly" type="button" @click="addItem(itemInputName); itemInputName=\'\'">Add</button>\
            <select class="item-class-filter" v-model="itemClassFilter">\
                <option v-for="itemClass in allowedItemClasses">{{ itemClass }}</option>\
            </select>\
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
                .concat(_.sortBy(GameData.data.itemCategories['weapons']))
                .concat(_.sortBy(GameData.data.itemCategories['armour']))
                .concat(_.sortBy(GameData.data.itemCategories['jewelry']))
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
            var ic = GameData.data.itemClasses[itemClass];
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

    props: ['item', 'itemStyle', 'deletable', 'itemRarity', 'itemClass'],

    computed: {
        style: function() {
            return Style.toCSS(Style.getEffectiveStyle(Style.data, this.itemStyle, this.itemRarity, this.itemClass));
        }
    },

    methods: {
        deleteItem: function() { this.$emit('deleted'); }
    }
});
