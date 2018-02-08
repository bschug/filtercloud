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
                });
        }
    }

    Config.load = function() {
        var config = new ConfigSettings();
        return config.load('default')
                     .then(function(response) { Config.current = config; })
                     .then(function(response) { Config.restore_session(); })
                     .catch(function(error) { console.error("Failed to load config: " + error); });
    };

    Config.restore_session = function() {
        var storedConfig = localStorage.getItem('poegg-filter-config');
        if (!storedConfig) {
            console.log("No previous filter config found");
            return;
        }
        Config.current.data = JSON.parse(storedConfig);
    };

    Config.persist_session = function() {
        console.log("I will remember that");
        localStorage.setItem('poegg-filter-config', JSON.stringify(Config.current.data));
    }

}( window.Config = window.Config || {} ));