(function(GameData) {
    GameData.data = {};
    GameData.baseTypeToItemClass = {};

    GameData.load = function() {
        return axios.get('/api/filter/game-constants')
            .then(function(response) {
                GameData.data = response.data;
                buildBaseTypeToItemClassIndex();
            })
    };

    function buildBaseTypeToItemClassIndex() {
        for (var itemClass in GameData.data.itemClasses) {
            var baseTypes = GameData.data.itemClasses[itemClass];
            for (var i=0; i < baseTypes.length; i++) {
                GameData.baseTypeToItemClass[baseTypes[i]] = itemClass;
            }
        }
    }

    GameData.getItemClass = function(baseType) {
        return GameData.baseTypeToItemClass[baseType];
    }

}( window.GameData = window.GameData || {} ));