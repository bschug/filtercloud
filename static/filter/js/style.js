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
}( window.Style = window.Style || {} ));