class StyleCollection(object):
    def __init__(self, default, styles):
        self._default = default
        self._styles = styles

    def __getattr__(self, name):
        return self._styles.get(name, self._default)

    def __str__(self):
        return str(self._default)


class ItemStyle(object):
    def __init__(self, textcolor=None, background=None, border=None, fontsize=None, sound=None):
        self.textcolor = textcolor
        self.background = background
        self.border = border
        self.fontsize = fontsize
        self.sound = sound

    def fill_with(self, defaults):
        """Apply default style without overriding anything set in this style (only overrides None entries)."""
        self.textcolor = defaults.textcolor if self.textcolor is None else self.textcolor.fill_with(defaults.textcolor)
        self.background = defaults.background if self.background is None else self.background.fill_with(defaults.background)
        self.border = defaults.border if self.border is None else self.border.fill_with(defaults.border)
        self.fontsize = defaults.fontsize if self.fontsize is None else self.fontsize
        self.sound = defaults.sound if self.sound is None else self.sound.fill_with(defaults.sound)
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
        if self.sound and not self.sound.positional:
            yield '    PlayAlertSound ' + str(self.sound)
        if self.sound and self.sound.positional:
            yield '    PlayAlertSoundPositional ' + str(self.sound)

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
    def __init__(self, soundid=None, volume=None, positional=None):
        self.soundid = soundid
        self.volume = volume
        self.positional = positional

    def fill_with(self, defaults):
        if defaults is None:
            return self
        self.soundid = self.soundid or defaults.soundid
        self.volume = self.volume or defaults.volume
        self.positional = self.positional if self.positional is not None else defaults.positional
        assert not any(x is None for x in (self.soundid, self.volume, self.positional))
        return self

    def __str__(self):
        if self.volume != 100:
            return '{} {}'.format(self.soundid, self.volume)
        else:
            return str(self.soundid)


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
        return Sound(soundid=parts, volume=100, positional=False)
    else:
        soundid, volume = parts
        return Sound(soundid=soundid, volume=volume, positional=False)