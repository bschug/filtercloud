(function( Item ) {

    Item.colorToCSS = function (text) {
        var r, g, b, a;
        var channels = text.trim().split(' ');
        if (len(channels) === 3) {
             r, g, b = channels;
             return 'rgb(' + r + ', ' + g + ', ' + b + ')';
        } else {
            r, g, b, a = channels;
            return 'rgba(' + r + ', ' + g + ', '+ b + ', ' + a + ')';
        }
    };

    Item.fontsizeToCSS = function (size) {
		var actualSize = MathUtils.remap( parseInt(size), 18, 45, 8, 24 );
		return (actualSize).toString() + 'px';
	};

}( window.Item = window.Item || {} ));