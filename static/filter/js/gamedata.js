(function(GameData) {
    GameData.itemCategories = {};  // category (all, weapons, armour, jewelry, etc) -> [itemClass]
    GameData.itemClasses = {};  // itemClass -> [baseType -> stats]
    GameData.baseTypes = {};  // baseType -> stats
    GameData.baseTypeToItemClass = {};  // baseType -> itemClass
    GameData.prices = {};  // currency|divcards|uniques -> { baseType -> price }
    GameData.leagues = [];
    GameData.allLeagues = [];
    GameData.leagueUniques = {} // league -> unique names

    GameData.load = function(league, uniqueLeagues) {
        var startTime = new Date();

        var constants = axios.get('/api/filter/game-constants')
            .then(function(response) {
                GameData.itemClasses = response.data.itemClasses;
                GameData.itemCategories = response.data.itemCategories;
                GameData.allLeagues = response.data.leagues;
                GameData.leagueUniques = response.data.leagueUniques;
                buildAllItemsCategory();
                buildBaseTypesIndex();
                buildBaseTypeToItemClassIndex();
                convertLeagueUniquesToSets();
            });

        var prices = GameData.loadPrices(league, uniqueLeagues);

        var leagues = axios.get('/api/filter/leagues')
            .then(function(response) {
                GameData.leagues = response.data;
            });

        return Promise.all([constants, prices, leagues])
            .then(function(response) {
                var duration = +new Date() - startTime;
                console.log("Load GameData complete after " + duration + " ms");
            })
            .catch(function(error) {
                console.log("Failed to load GameData:", error);
            });
    };

    GameData.loadPrices = function(league, uniqueLeagues) {
        return axios.get('/api/filter/prices/' + league)
            .then(function(response) {
                GameData.prices = response.data;
            });
    }

    function buildAllItemsCategory() {
        var result = [];
        for (var k in GameData.itemCategories) {
            result = result.concat(GameData.itemCategories[k]);
        }
        GameData.itemCategories.all = result;
    }

    function buildBaseTypesIndex() {
        for (var itemClass in GameData.itemClasses) {
            for (var baseType in GameData.itemClasses[itemClass]) {
                GameData.baseTypes[baseType] = GameData.itemClasses[itemClass][baseType];
            }
        }
    }

    function buildBaseTypeToItemClassIndex() {
        for (var itemClass in GameData.itemClasses) {
            for (var baseType in GameData.itemClasses[itemClass]) {
                GameData.baseTypeToItemClass[baseType] = itemClass;
            }
        }
    }

    function convertLeagueUniquesToSets() {
        for (var league in Object.keys(GameData.leagueUniques)) {
            GameData.leagueUniques[league] = new Set(GameData.leagueUniques[league]);
        }
    }

    GameData.getItemClass = function(baseType) {
        return GameData.baseTypeToItemClass[baseType];
    }

}( window.GameData = window.GameData || {} ));