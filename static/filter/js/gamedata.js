(function(GameData) {
    GameData.data = {};

    GameData.load = function() {
        return axios.get('/api/filter/game-constants')
            .then(function(response) {
                GameData.data = response.data;
            })
    }

}( window.GameData = window.GameData || {} ));