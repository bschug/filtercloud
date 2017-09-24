(function(GameData) {
    GameData.itemCategories = {};  // category (weapons, armour, jewelry, etc) -> [itemClass]
    GameData.itemClasses = {};  // itemClass -> [baseType]
    GameData.baseTypeToItemClass = {};  // baseType -> itemClass
    GameData.prices = {};  // currency|divcards|uniques -> { baseType -> price }

    GameData.load = function(league) {
        var startTime = +new Date();

        var constants = axios.get('/api/filter/game-constants')
            .then(function(response) {
                GameData.itemClasses = response.data.itemClasses;
                GameData.itemCategories = response.data.itemCategories;
                buildBaseTypeToItemClassIndex();
            });

        var prices = axios.get('/api/filter/prices/' + league)
            .then(function(response) {
                GameData.prices = response.data;
            });

        return Promise.all([constants, prices])
            .then(function(response) {
                var duration = +new Date() - startTime;
                console.log("Load GameData complete after " + duration + " ms");
            })
            .catch(function(error) {
                console.log("Failed to load GameData:", error);
            });
    };

    function buildBaseTypeToItemClassIndex() {
        for (var itemClass in GameData.itemClasses) {
            var baseTypes = GameData.itemClasses[itemClass];
            for (var i=0; i < baseTypes.length; i++) {
                GameData.baseTypeToItemClass[baseTypes[i]] = itemClass;
            }
        }
    }

    GameData.getItemClass = function(baseType) {
        return GameData.baseTypeToItemClass[baseType];
    }

}( window.GameData = window.GameData || {} ));