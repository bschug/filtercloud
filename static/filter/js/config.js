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
                     .catch(function(error) { console.error("Failed to load config: " + error); });
    };
}( window.Config = window.Config || {} ));