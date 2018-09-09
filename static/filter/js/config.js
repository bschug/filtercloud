(function(Config) {
    Config.owner = '';
    Config.name = '';
    Config.data = null;

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

    Config.load = function(id) {
        Config.owner = '';
        Config.name = '';

        var path = '';
        if (id) {
            path = id.owner + '/' + id.name;
            Config.owner = id.owner;
            Config.name = id.name;
        }

        return axios.get('/api/filter/config/' + path)
            .then(function(response) {
                console.log("Loaded config " + id);
                Config.data = response.data;
            })
            .then(function(response) {
                // Restore session only if we're not explicitly loading a different config
                // We need to do this after we've loaded the filter to be able to detect
                // breaking changes in the filter format.
                if (path === '') {
                    Config.restore_session();
                }
            })
            .catch(function(error) {
                console.error("Failed to load Config: ", error);
                alert("Failed to load Config: " + path);
                if (id !== 'default') {
                    console.log("Loading default Config instead");
                    return Config.load();
                }
            })
    };

    Config.save = function(name) {
        Config.owner = UserSession.username;
        Config.name = name;

        var formData = new FormData();
        formData.append('token', UserSession.getSessionToken());
        formData.append('data', JSON.stringify(Config.data));

        var path = '/api/filter/config/' + UserSession.username + '/' + Config.name;

        axios.post(path, formData)
        .then(function(response) {
            console.log("Config " + Config.name + " saved successfully");
            UserSession.configs = response.data;
            alert("Saved as " + Config.name);
        })
        .catch(function(response) {
            console.error("Failed to save config");
            console.error(response);
            alert("Failed to save config");
        });
    };

    Config.restore_session = function() {
        var storedConfig = localStorage.getItem('poegg-filter-config');
        if (!storedConfig) {
            console.log("No previous filter config found");
            return;
        }
        storedConfig = JSON.parse(storedConfig);
        ObjectUtils.addMissingKeys(storedConfig, Config.data);
        Config.data = storedConfig;
        console.log("Restored config from saved session");
    };

    Config.persist_session = function() {
        console.log("I will remember that");
        localStorage.setItem('poegg-filter-config', JSON.stringify(Config.data));
    }

}( window.Config = window.Config || {} ));