# -*- coding: utf-8 -*-

__version__ = "0.2.1"

from .pastel import Pastel


_PASTEL = Pastel(True)


def colorize(message):
    """
    Formats a message to a colorful string.

    :param message: The message to format.
    :type message: str

    :rtype: str
    """
    with _PASTEL.colorized():
        return _PASTEL.colorize(message)


def with_colors(colorized):
    """
    Enable or disable colors.

    :param decorated: Whether to active colors or not.
    :type decorated: bool

    :rtype: None
    """
    _PASTEL.with_colors(colorized)


def add_style(name, fg=None, bg=None, options=None):
    """
    Adds a new style.

    :param name: The name of the style
    :type name: str

    :param fg: The foreground color
    :type fg: str or None

    :param bg: The background color
    :type bg: str or None

    :param options: The style options
    :type options: list or str or None
    """
    _PASTEL.add_style(name, fg, bg, options)


def remove_style(name):
    """
    Removes a style.

    :param name: The name of the style to remove.
    :type name: str

    :rtype: None
    """
    _PASTEL.remove_style(name)


def pastel(colorized=True):
    """
    Returns a new Pastel instance.

    :rtype: Pastel
    """
    return Pastel(colorized)
