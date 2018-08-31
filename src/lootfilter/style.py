class StyleCollection(object):
    def __init__(self, default, styles):
        self._default = default
        self._styles = styles

    def __getattr__(self, name):
        return self._styles.get(name, self._default)

    def __str__(self):
        return str(self._default)


class ItemStyle(object):
    def __init__(self, textcolor=None, background=None, border=None, fontsize=None, sound=None, disable_drop_sound=None, map_icon=None, beam=None):
        self.textcolor = textcolor
        self.background = background
        self.border = border
        self.fontsize = fontsize
        self.sound = sound
        self.disable_drop_sound = disable_drop_sound
        self.map_icon = map_icon
        self.beam = beam

    def fill_with(self, defaults):
        """Apply default style without overriding anything set in this style (only overrides None entries)."""
        self.textcolor = defaults.textcolor if self.textcolor is None else self.textcolor.fill_with(defaults.textcolor)
        self.background = defaults.background if self.background is None else self.background.fill_with(defaults.background)
        self.border = defaults.border if self.border is None else self.border.fill_with(defaults.border)
        self.fontsize = defaults.fontsize if self.fontsize is None else self.fontsize
        self.sound = defaults.sound if self.sound is None else self.sound.fill_with(defaults.sound)
        self.disable_drop_sound = defaults.disable_drop_sound if self.disable_drop_sound is None else self.disable_drop_sound
        self.map_icon = defaults.map_icon if self.map_icon is None else self.map_icon.fill_with(defaults.map_icon)
        self.beam = defaults.beam if self.beam is None else self.beam.fill_with(defaults.beam)
        return self

    def generate(self):
        if self.textcolor:
            yield '    SetTextColor ' + str(self.textcolor)
        if self.background:
            yield '    SetBackgroundColor ' + str(self.background)
        if self.border:
            yield '    SetBorderColor ' + str(self.border)
        if self.fontsize:
            yield '    SetFontSize ' + str(self.fontsize)
        if self.sound:
            yield '    ' + str(self.sound)
        if self.disable_drop_sound:
            yield '    DisableDropSound'
        if self.map_icon:
            yield '    MinimapIcon ' + str(self.map_icon)
        if self.beam:
            yield '    PlayEffect ' + str(self.beam)

    def __str__(self):
        return '\n'.join(self.generate())


class Color(object):
    def __init__(self, red=None, green=None, blue=None, alpha=None):
        self.red = red
        self.green = green
        self.blue = blue
        self.alpha = alpha

    def fill_with(self, defaults):
        if defaults is None:
            return self
        self.red = self.red or defaults.red
        self.green = self.green or defaults.green
        self.blue = self.blue or defaults.blue
        self.alpha = self.alpha or defaults.alpha
        assert not any(x is None for x in (self.red, self.green, self.blue, self.alpha))
        return self

    def __str__(self):
        if self.alpha < 255:
            return '{} {} {} {}'.format(self.red, self.green, self.blue, self.alpha)
        else:
            return '{} {} {}'.format(self.red, self.green, self.blue)


class Sound(object):
    def __init__(self, soundid=None, volume=None, positional=None, custom=None):
        self.soundid = soundid
        self.volume = volume
        self.positional = positional
        self.custom = custom

    def fill_with(self, defaults):
        if defaults is None:
            return self
        self.soundid = self.soundid or defaults.soundid
        self.volume = self.volume or defaults.volume
        self.positional = self.positional if self.positional is not None else defaults.positional
        self.custom = self.custom if self.custom is not None else defaults.custom
        assert not any(x is None for x in (self.soundid, self.volume, self.positional, self.custom))
        return self

    def __str__(self):
        if self.custom:
            return 'CustomAlertSound "{}"'.format(self.soundid)

        action = 'PlayAlertSoundPositional' if self.positional else 'PlayAlertSound'
        if self.volume != 100:
            return '{} {} {}'.format(action, self.soundid, self.volume)
        else:
            return '{} {}'.format(action, self.soundid)


class MapIcon(object):
    def __init__(self, size=None, color=None, shape=None):
        self.size = size
        self.color = color
        self.shape = shape

    def fill_with(self, defaults):
        if defaults is None:
            return self
        self.size = self.size if self.size is not None else defaults.size
        self.color = self.color if self.color is not None else defaults.color
        self.shape = self.shape if self.shape is not None else defaults.shape
        assert not any(x is None for x in (self.size, self.color, self.shape))
        return self

    def __str__(self):
        return '{} {} {}'.format(self.size, self.color, self.shape)


class Beam(object):
    def __init__(self, color=None, temp=None):
        self.color = color
        self.temp = temp

    def fill_with(self, defaults):
        if defaults is None:
            return self
        self.color = self.color if self.color is not None else defaults.color
        self.temp = self.temp if self.temp is not None else defaults.temp
        assert self.color is not None
        return self

    def __str__(self):
        if self.temp:
            return '{} Temp'.format(self.color)
        return self.color


def parse_color(text):
    if isinstance(text, Color):
        return text

    if text is None:
        return None

    parts = text.split()
    if len(parts) == 3:
        r, g, b = parts
        return Color(r, g, b, 255)
    else:
        r, g, b, a = parts
        return Color(r, g, b, int(a))


def parse_sound(text):
    if isinstance(text, Sound):
        return text

    if text is None:
        return None

    parts = text.split()
    if len(parts) == 1:
        return Sound(soundid=parts, volume=100, positional=False, custom=False)
    else:
        soundid, volume = parts
        return Sound(soundid=soundid, volume=volume, positional=False, custom=False)


def parse_map_icon(obj):
    if isinstance(obj, MapIcon):
        return obj

    if obj is None:
        return None

    return MapIcon(size=obj.get('size'), color=obj.get('color'), shape=obj.get('shape'))


def parse_beam(obj):
    if isinstance(obj, Beam):
        return obj

    if obj is None:
        return None

    return Beam(color=obj.get('color'), temp=obj.get('temp'))
