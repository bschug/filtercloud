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
                    v-for="item in items" :key="item" \
                    :item="item" :item-style="itemStyle" :item-rarity="itemRarity" :item-class="itemClass" \
                    :deletable="true" @deleted="deleteItem(item)"/>\
            </div>\
            <input type="text" v-model="itemInputName">\
            <button type="button" @click="addItem(itemInputName)">Add</button>\
        </div>',
    props: ['title', 'items', 'itemStyle', 'itemRarity', 'itemClass'],
    data: function() { return { 'itemInputName': '' } },
    methods: {
        deleteItem: function(item) { this.$emit('update:items', this.items.filter(function(x) { return x !== item; })); },
        addItem: function(item) { this.items.push(item); }
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
})