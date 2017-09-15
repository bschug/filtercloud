(function( Style ) {
    Style.data = null;

    Style.load = function() {
        return axios.get('/api/filter/style/default')
            .then(function(response) {
                console.log("Loaded default style");
                Style.data = response.data;
            })
            .catch(function(error) {
                console.error("Failed to load Style: ", error);
            });
    };

    Style.toCSS = function(stylesheet, identifier) {
        // TODO actually use stylesheet

        // scale font size from ingame units to css units
        var fontSize = 45;
        fontSize = MathUtils.remap(fontSize, 18, 45, 10, 24);

        // scale height with font size, but keep a minimum and maximum margin
        var height = Math.round(fontSize * 1.15);
        height = MathUtils.clamp(height, fontSize + 2, fontSize + 5);

        return {
            borderStyle: 'solid',
            borderWidth: '1px',
            borderColor: 'rgb(200, 200, 200)',
            backgroundColor: 'rgba(0, 0, 0, 50)',
            color: 'rgb(200, 200, 200)',
            fontSize: '' + fontSize + 'px',
            height: '' + height + 'px'
        };
    };
}( window.Style = window.Style || {} ));