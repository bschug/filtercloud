(function(Config) {
    Config.current = null;

    function ConfigSettings() {
        this.data = null;

        this.load = function(id) {
            var self = this;
            return axios.get('/api/filter/config/' + id)
                .then(function(response) {
                    console.log("Loaded config " + id);
                    self.data = response.data;
                })
                .catch(function(error) {
                    console.error("Failed to load Config: ", error);
                    if (id !== 'default') {
                        console.log("Loading default Config instead");
                        return self.load('default');
                    }
                });
        }
    }

    Config.load = function(name) {
        if (name === undefined) {
            name = 'default';
        }

        var config = new ConfigSettings();
        return config.load(name)
                     .then(function(response) { Config.current = config; })
                     .then(function(response) { if (name === 'default') { Config.restore_session(); } })
                     .catch(function(error) { console.error("Failed to load config: ", error); });
    };

    Config.restore_session = function() {
        var storedConfig = localStorage.getItem('poegg-filter-config');
        if (!storedConfig) {
            console.log("No previous filter config found");
            return;
        }
        storedConfig = JSON.parse(storedConfig);
        if (storedConfig.version !== Config.current.data.version) {
            alert("A new version of the filter is available. Your stored settings have been reset to default.");
            return;
        }
        Config.current.data = storedConfig;
        console.log("Restored config from saved session");
    };

    Config.persist_session = function() {
        console.log("I will remember that");
        localStorage.setItem('poegg-filter-config', JSON.stringify(Config.current.data));
    }

}( window.Config = window.Config || {} ));