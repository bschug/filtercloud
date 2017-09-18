(function( FilterCloud ) {
    FilterCloud.app = null;

    FilterCloud.init = function() {
        console.log("Loading files before init...");
        Promise.all([Style.load(), Config.load(), GameData.load()])
        .then(function() {
            console.log("Initializing now...")
            FilterCloud.app = new Vue({
                el: '#page',
                data: {
                    style: Style.data,
                    config: Config.current.data,
                    gameData: GameData.data,
                    currentPage: null,
                },
                watch: {
                    'config.currency.ultra_rare': 'updateNormalCurrency',
                    'config.currency.strong_highlight': 'updateNormalCurrency',
                    'config.currency.highlight': 'updateNormalCurrency',
                    'config.currency.smaller': 'updateNormalCurrency'
                },
                methods: {
                    updateNormalCurrency: function() {
                        console.log("Update Normal Currency");
                        var self = this;
                        var normalCurrencies = [];
                        for (var i=0; i < GameData.data.itemCategories.currency.length; i++) {
                            var itemClass = GameData.data.itemCategories.currency[i];
                            var baseTypes = GameData.data.itemClasses[itemClass];
                            for (var j=0; j < baseTypes.length; j++) {
                                if (self.config.currency.ultra_rare.indexOf(baseTypes[j]) >= 0) {
                                    console.log("   " + baseTypes[j] + " is ultra_rare");
                                }
                                else if (self.config.currency.strong_highlight.indexOf(baseTypes[j]) >= 0) {
                                    console.log("   " + baseTypes[j] + " is strong_highlight");
                                }
                                else if (self.config.currency.highlight.indexOf(baseTypes[j]) >= 0) {
                                    console.log("   " + baseTypes[j] + " is highlight");
                                }
                                else if (self.config.currency.smaller.indexOf(baseTypes[j]) >= 0) {
                                    console.log("   " + baseTypes[j] + " is smaller");
                                }
                                else {
                                    normalCurrencies.push(baseTypes[j]);
                                }
                            }
                        }
                        this.config.currency.normal = normalCurrencies;
                        console.log("Normal currencies: ", normalCurrencies);
                    }
                }
            });
        });
    };

}( window.FilterCloud = window.FilterCloud || {} ));