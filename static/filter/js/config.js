(function(Config) {
    Config.current = null;
    Config.endgame = null;
    Config.leveling = null;

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
        var loads = [];
        var endgame = new ConfigSettings();
        loads.push(endgame.load('endgame')
            .then(function(response) { Config.endgame = endgame; }));

        var leveling = new ConfigSettings();
        loads.push(leveling.load('leveling')
            .then(function(response) { Config.leveling = leveling; }));

        return Promise.all(loads);
    };
}( window.Config = window.Config || {} ));