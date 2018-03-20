(function( Style ) {
    Style.data = null;
    Style.owner = '';
    Style.name = '';

    // Default styles the game uses when the filter doesn't override it
    Style.defaultStyle = function(rarity, itemClass) {
        result = {
            'textcolor': '200 200 200',
            'background': '0 0 0 190',
            'fontsize': '32',
            'border': '',
            'sound': ''
        };
        if (rarity === 'magic')
            result.textcolor = '136 136 255';
        else if (rarity === 'rare')
            result.textcolor = '255 255 119';
        else if (rarity === 'unique')
            result.textcolor = '175 96 37';

        if (itemClass === 'Currency' || itemClass === 'Stackable Currency' || itemClass === 'Leaguestones'
            || itemClass === 'Labyrinth Trinket' || itemClass === 'Misc Map Items')
            result.textcolor = '170 158 130';
        else if (itemClass === 'Divination Card')
            result.textcolor = '14 186 255';
        else if (itemClass === 'Active Skill Gems' || itemClass === 'Support Skill Gems')
            result.textcolor = '27 162 155';
        else if (itemClass === 'Quest Items' || itemClass === 'Labyrinth Item')
            result.textcolor = '74 230 58';
        else if (itemClass === 'Maps' || itemClass == 'Map Fragments')
            result.border = result.textcolor;
        else if (itemClass === 'Piece')
            result.textcolor = '175 96 37';

        return result;
    };

    Style.load = function(id) {
        Style.owner = '';
        Style.name = '';

        var path = '';
        if (id) {
            path = owner + '/' + name;
            Style.owner = id.owner;
            Style.name = id.name;
        }

        return axios.get('/api/filter/style/' + path)
            .then(function(response) {
                console.log("Loaded style: " + path);
                Style.data = response.data;
            })
            .catch(function(error) {
                console.error("Failed to load Style: ", error);
                alert("Failed to load Style: " + path);
                if (id !== 'default') {
                    console.log("Loading default style instead");
                    return Style.load();
                }
            });
    };

    Style.toCSS = function(style, isHidden) {
        var result = {
            borderStyle: 'none',
            borderWidth: '1px',
            backgroundColor: 'rgba(0, 0, 0, 50)',
            color: 'rgb(200, 200, 200)',
        };

        // scale font size from ingame units to css units
        var fontSize = parseInt(style.fontsize);
        fontSize = MathUtils.remap(fontSize, 18, 45, 10, 24);
        result.fontSize = '' + fontSize + 'px';

        // scale height with font size, but keep a minimum and maximum margin
        var height = Math.round(fontSize * 1.15);
        height = MathUtils.clamp(height, fontSize + 2, fontSize + 5);
        result.height = '' + height + 'px';

        if (style.border !== null && style.border.length > 0) {
            result.borderStyle = 'solid';
            result.borderColor = Style.colorToCSS(style.border);
        }

        result.color = Style.colorToCSS(style.textcolor);
        result.backgroundColor = Style.colorToCSS(style.background);

        if (isHidden) {
            result.textDecoration = 'line-through';
            result.opacity = 0.5;
        }

        return result;
    };

    Style.colorToCSS = function(color) {
        color = color.split(' ');
        if (color.length === 3) {
            return "rgb(" + color[0] + "," + color[1] + "," + color[2] + ")";
        } else {
            return "rgba(" + color[0] + "," + color[1] + "," + color[2] + "," + color[3] + ")";
        }
    }

    /* Fill all empty stats with parent default or rarity default. */
    Style.getEffectiveStyle = function(stylesheet, identifier, rarity, itemClass, isHidden) {
        if (rarity) {
            rarities = rarity.split(',');
            rarity = rarities[Math.floor((Math.random() * rarities.length))]
        } else {
            rarity = "normal";
        }

        var parts = identifier.split('.');
        if (parts.length == 0 || parts.length > 2) {
            throw "Invalid style identifier: " + identifier;
        }
        var styleName = parts[0];
        var context = parts.length == 1 ? 'default' : parts[1];

        if (!(styleName in stylesheet)) {
            console.error("Unknown Style: ", styleName, " -- from identifier: ", identifier);
        }

        if (!('default' in stylesheet[styleName])) {
            console.error("Style " + styleName + " has no default!");
        }

        var result = Style.defaultStyle(rarity, itemClass);
        var styleDefault = stylesheet[styleName].default;

        for (var key in styleDefault) {
            if (styleDefault[key] != null) {
                result[key] = styleDefault[key];
            }
        }
        if (context in stylesheet[styleName]) {
            var styleSpecialized = stylesheet[styleName][context];
            for (var key in styleSpecialized) {
                if (styleSpecialized[key] != null) {
                    result[key] = styleSpecialized[key];
                }
            }
        }

        return result;
    };


}( window.Style = window.Style || {} ));