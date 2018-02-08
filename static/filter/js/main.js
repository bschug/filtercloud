(function( FilterCloud ) {
    FilterCloud.app = null;

    FilterCloud.init = function() {
        console.log("Loading files before init...");
        Promise.all([Style.load(), Config.load(), GameData.load('Standard')])
        .then(function() {
            console.log("Initializing now...")
            FilterCloud.app = new Vue({
                el: '#page-root',
                data: {
                    style: Style.data,
                    config: Config.current.data,
                    currentPage: null,
                    GameData: GameData,
                    selectedLeague: 'Standard',
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

                        ga('send', 'event', 'download', 'start');
                        console.log(JSON.parse(JSON.stringify(Config.current.data)));

                        axios.post('/api/filter/build', formData, {
                            responseType: 'arraybuffer'
                        })
                        .then(function(response) {
                            var blob = new Blob([response.data], { type: 'text/plain' });
                            console.log("Downloaded " + (blob.size / 1024).toFixed(2) + "kB filter file");

                            ga('send', 'event', 'download', 'success');

                            var link = document.createElement('a');
                            // workaround for old browsers
                            if (typeof link.download === 'undefined') {
                                console.log("WORKAROUND");
                                window.location = downloadUrl;
                            } else {
                                link.href = window.URL.createObjectURL(blob);
                                link.download = 'poe.gg.filter';
                                document.body.appendChild(link);
                                link.click();
                            }
                        })
                        .catch(function(error) {
                            console.log("Download failed with error: ", error);
                            ga('send', 'event', 'download', 'error');
                        });
                    },

                    give_feedback: function() {
                        ga('send', 'event', 'feedback');
                        window.location = 'https://www.reddit.com/message/compose/?to=bschug';
                    }
                },

                watch: {
                    selectedLeague: function() {
                        GameData.loadPrices(this.selectedLeague)
                            .then(function() {
                                console.log("Received new prices");
                                this.GameData = GameData;
                                this.allUniqueItems = Object.keys(GameData.prices.uniques).sort();
                            })
                            .catch(function(error) {
                                console.error("Failed to load prices for ", league, ": ", error);
                            });
                    },

                    config: {
                        handler: function() {
                            console.log("Config Changed");
                            Config.persist_session();
                        },
                        deep: true
                    }
                }
            });
        });
    };

}( window.FilterCloud = window.FilterCloud || {} ));