(function( FilterCloud ) {
    FilterCloud.app = null;

    FilterCloud.init = function() {
        console.log("Loading files before init...");
        Promise.all([Style.load(), Config.load(), GameData.load('Harbinger')])
        .then(function() {
            console.log("Initializing now...")
            FilterCloud.app = new Vue({
                el: '#page',
                data: {
                    style: Style.data,
                    config: Config.current.data,
                    currentPage: null,
                    GameData: GameData
                },
                methods: {
                    setCurrencyOverride: function(item, tier) {
                        console.log("Currency override:", item, tier);
                        config.currency.overrides[item] = tier;
                    }
                }
            });
        });
    };

}( window.FilterCloud = window.FilterCloud || {} ));