(function( FilterCloud ) {
    FilterCloud.app = null;

    FilterCloud.init = function() {
        console.log("Loading files before init...");
        Promise.all([Style.load(), Config.load(), GameData.load('Harbinger')])
        .then(function() {
            console.log("Initializing now...")
            FilterCloud.app = new Vue({
                el: '#page-root',
                data: {
                    style: Style.data,
                    config: Config.current.data,
                    currentPage: null,
                    GameData: GameData,
                    allUniqueItems: Object.keys(GameData.prices.uniques).sort()
                },
                methods: {

                    setCurrencyOverride: function(item, tier) {
                        console.log("Currency override:", item, tier);
                        config.currency.overrides[item] = tier;
                    },

                    downloadFilter: function() {
                        var formData = new FormData();
                        formData.append('style', JSON.stringify(Style.data));
                        formData.append('config', JSON.stringify(Config.current.data));

                        axios.post('/api/filter/build', formData, {
                            responseType: 'arraybuffer'
                        })
                        .then(function(response) {
                            var blob = new Blob([response.data], { type: 'text/plain' });
                            var link = document.createElement('a');
                            link.href = window.URL.createObjectURL(blob);
                            link.download = Config.current.data.include_leveling_rules ? 'gg-leveling.filter' : 'gg-endgame.filter';
                            link.click();
                        });
                    }
                }
            });
        });
    };

}( window.FilterCloud = window.FilterCloud || {} ));