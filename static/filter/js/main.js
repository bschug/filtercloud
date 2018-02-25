(function( FilterCloud ) {
    FilterCloud.app = null;

    FilterCloud.init = function() {
        console.log("Loading files before init...");
        var settings = FilterCloud.parseUrlParams();
        console.log("Settings:", settings);

        Promise.all([Style.load(settings.style), Config.load(settings.config), GameData.load('Standard')])
        .then(function() {
            console.log("Initializing now...");
            FilterCloud.app = new Vue({
                el: '#page-root',
                data: {
                    style: Style.data,
                    styleName: Style.name,
                    config: Config.data,
                    configName: Config.name,
                    currentPage: null,
                    GameData: GameData,
                    selectedLeague: 'Standard',
                    allUniqueItems: Object.keys(GameData.prices.uniques).sort(),
                    UserSession: window.UserSession
                },
                methods: {

                    setCurrencyOverride: function(item, tier) {
                        console.log("Currency override:", item, tier);
                        config.currency.overrides[item] = tier;
                    },

                    downloadFilter: function() {
                        var formData = new FormData();
                        formData.append('style', JSON.stringify(Style.data));
                        formData.append('config', JSON.stringify(Config.data));

                        ga('send', 'event', 'download', 'start');
                        console.log(JSON.parse(JSON.stringify(Config.data)));

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

                    saveConfig: Config.save,
                    loadConfig: Config.load,
                    saveStyle: Style.save,
                    loadStyle: Style.load,

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

    FilterCloud.parseUrlParams = function() {
        var result = {
            config: null,
            style: null
        };

        // Filter config name can be passed as url like https://filter.poe.gg#username/filtername?style=stylename
        var hash = window.location.hash;
        var re = /#([a-z0-9][a-z0-9\-]*[a-z0-9])\/([a-z0-9][a-z0-9\-.]*[a-z0-9])?\??(.*)?/;
        var match = hash.match(re);

        // If url doesn't have that form, use the default filter
        if (match === null) {
            return result;
        }

        // If url contains a config name, use that one
        if (match[1] && match[2]) {
            result.config = {
                owner: match[1],
                name: match[2]
            }
        }

        function parseQuery(query) {
            var match = query.match(/([a-z]*)=(.*)/);
            if (!match || !match[1] || !match[2]) { return null; }

            var key = match[1];
            if (key === 'style') {
                return {key: 'style', value: parseStyle(match[2])};
            }
        }

        function parseStyle(text) {
            var re = /^([a-z0-9][a-z0-9\-]*[a-z0-9])\/([a-z0-9][a-z0-9\-.]*[a-z0-9])$/;
            var match = text.match(re);
            if (!match || !match[1] || !match[2]) {
                return null;
            }
            return { owner: match[1], name: match[2] };
        }

        // If result contains a query string, parse it further
        if (match[3]) {
            match[3].split('&').forEach(function(query) {
                var kv = parseQuery(query);
                if (kv) {
                    result[kv.key] = kv.value;
                }
            })
        }

        return result;
    };

}( window.FilterCloud = window.FilterCloud || {} ));