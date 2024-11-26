# -*- coding: utf-8 -*-

import re
import sys
from contextlib import contextmanager

from .style import Style
from .stack import StyleStack


class Pastel(object):

    TAG_REGEX = "[a-z][a-z0-9,_=;-]*"
    FULL_TAG_REGEX = re.compile("(?isx)<(({}) | /({})?)>".format(TAG_REGEX, TAG_REGEX))

    def __init__(self, colorized=False):
        self._colorized = colorized
        self._style_stack = StyleStack()
        self._styles = {}

        self.add_style("error", "white", "red")
        self.add_style("info", "green")
        self.add_style("comment", "yellow")
        self.add_style("question", "black", "cyan")

    @classmethod
    def escape(cls, text):
        return re.sub("(?is)([^\\\\]?)<", "\\1\\<", text)

    @contextmanager
    def colorized(self, colorized=None):
        is_colorized = self.is_colorized()

        if colorized is None:
            colorized = sys.stdout.isatty() and is_colorized

        self.with_colors(colorized)

        yield

        self.with_colors(is_colorized)

    def with_colors(self, colorized):
        self._colorized = colorized

    def is_colorized(self):
        return self._colorized

    def add_style(self, name, fg=None, bg=None, options=None):
        style = Style(fg, bg, options)

        self._styles[name] = style

    def has_style(self, name):
        return name in self._styles

    def style(self, name):
        if self.has_style(name):
            return self._styles[name]

    def remove_style(self, name):
        if not self.has_style(name):
            raise ValueError("Invalid style {}".format(name))

        del self._styles[name]

    def colorize(self, message):
        output = ""
        tags = []
        i = 0
        for m in self.FULL_TAG_REGEX.finditer(message):
            if i > 0:
                p = tags[i - 1]
                tags[i - 1] = (p[0], p[1], p[2], p[3], m.start(0))

            tags.append((m.group(0), m.end(0), m.group(1), m.group(3), None))

            i += 1

        if not tags:
            return message.replace("\\<", "<")

        offset = 0
        for t in tags:
            prev_offset = offset
            offset = t[1]
            endpos = t[4] if t[4] else -1
            text = t[0]
            if prev_offset < offset - len(text):
                output += self._apply_current_style(
                    message[prev_offset : offset - len(text)]
                )

            if offset != 0 and "\\" == message[offset - len(text) - 1]:
                output += self._apply_current_style(text)
                continue

            # opening tag?
            open = "/" != text[1]
            if open:
                tag = t[2]
            else:
                tag = t[3] if t[3] else ""

            style = self._create_style_from_string(tag.lower())
            if not open and not tag:
                # </>
                self._style_stack.pop()
            elif style is False:
                output += self._apply_current_style(text)
            elif open:
                self._style_stack.push(style)
            else:
                self._style_stack.pop(style)

            # add the text up to the next tag
            output += self._apply_current_style(message[offset:endpos])
            offset += len(message[offset:endpos])

        output += self._apply_current_style(message[offset:])

        return output.replace("\\<", "<")

    def _create_style_from_string(self, string):
        if string in self._styles:
            return self._styles[string]

        matches = re.findall("([^=]+)=([^;]+)(;|$)", string.lower())
        if not len(matches):
            return False

        style = Style()

        for match in matches:
            if match[0] == "fg":
                style.set_foreground(match[1])
            elif match[0] == "bg":
                style.set_background(match[1])
            else:
                try:
                    for option in match[1].split(","):
                        style.set_option(option.strip())
                except ValueError:
                    return False

        return style

    def _apply_current_style(self, text):
        if self.is_colorized() and len(text):
            return self._style_stack.get_current().apply(text)
        else:
            return text
