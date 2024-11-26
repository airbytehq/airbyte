# -*- coding: utf-8 -*-

from collections import OrderedDict


class Style(object):

    FOREGROUND_COLORS = {
        "black": 30,
        "red": 31,
        "green": 32,
        "yellow": 33,
        "blue": 34,
        "magenta": 35,
        "cyan": 36,
        "light_gray": 37,
        "default": 39,
        "dark_gray": 90,
        "light_red": 91,
        "light_green": 92,
        "light_yellow": 93,
        "light_blue": 94,
        "light_magenta": 95,
        "light_cyan": 96,
        "white": 97,
    }

    BACKGROUND_COLORS = {
        "black": 40,
        "red": 41,
        "green": 42,
        "yellow": 43,
        "blue": 44,
        "magenta": 45,
        "cyan": 46,
        "light_gray": 47,
        "default": 49,
        "dark_gray": 100,
        "light_red": 101,
        "light_green": 102,
        "light_yellow": 103,
        "light_blue": 104,
        "light_magenta": 105,
        "light_cyan": 106,
        "white": 107,
    }

    OPTIONS = {
        "bold": 1,
        "dark": 2,
        "italic": 3,
        "underline": 4,
        "blink": 5,
        "reverse": 7,
        "conceal": 8,
    }

    def __init__(self, foreground=None, background=None, options=None):
        self._fg = foreground
        self._bg = background
        self._foreground = None
        self._background = None

        if foreground:
            self.set_foreground(foreground)

        if background:
            self.set_background(background)

        options = options or []
        if not isinstance(options, list):
            options = [options]

        self.set_options(options)

    @property
    def foreground(self):
        return self._fg

    @property
    def background(self):
        return self._bg

    @property
    def options(self):
        return list(self._options.values())

    def set_foreground(self, foreground):
        if foreground not in self.FOREGROUND_COLORS:
            raise ValueError(
                'Invalid foreground specified: "{}". Expected one of ({})'.format(
                    foreground, ", ".join(self.FOREGROUND_COLORS.keys())
                )
            )

        self._foreground = self.FOREGROUND_COLORS[foreground]

    def set_background(self, background):
        if background not in self.FOREGROUND_COLORS:
            raise ValueError(
                'Invalid background specified: "{}". Expected one of ({})'.format(
                    background, ", ".join(self.BACKGROUND_COLORS.keys())
                )
            )

        self._background = self.BACKGROUND_COLORS[background]

    def set_option(self, option):
        if option not in self.OPTIONS:
            raise ValueError(
                'Invalid option specified: "{}". Expected one of ({})'.format(
                    option, ", ".join(self.OPTIONS.keys())
                )
            )

        if option not in self._options:
            self._options[self.OPTIONS[option]] = option

    def unset_option(self, option):
        if not option in self.OPTIONS:
            raise ValueError(
                'Invalid option specified: "{}". Expected one of ({})'.format(
                    option, ", ".join(self.OPTIONS.keys())
                )
            )

        del self._options[self.OPTIONS[option]]

    def set_options(self, options):
        self._options = OrderedDict()

        for option in options:
            self.set_option(option)

    def apply(self, text):
        codes = []

        if self._foreground:
            codes.append(self._foreground)

        if self._background:
            codes.append(self._background)

        if len(self._options):
            codes += list(self._options.keys())

        if not len(codes):
            return text

        return "\033[%sm%s\033[0m" % (";".join(map(str, codes)), text)

    def __eq__(self, other):
        return (
            other._foreground == self._foreground
            and other._background == self._background
            and other._options == self._options
        )
