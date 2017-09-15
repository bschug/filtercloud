(function( FilterCloud ) {
    FilterCloud.app = null;

    FilterCloud.init = function() {
        console.log("Loading files before init...");
        Promise.all([Style.load(), Config.load(), GameData.load()])
        .then(function() {
            console.log("Initializing now...")
            FilterCloud.app = new Vue({
                el: '#page',
                data: {
                    style: Style.data,
                    config: Config.current.data,
                    gameData: GameData.data,
                    currentPage: null,
                }
            });
        });
    };

}( window.FilterCloud = window.FilterCloud || {} ));