# Python
#
# This module implements a text class that allows to modify and create text on Markdown files.
#
# This file is part of mdutils. https://github.com/didix21/mdutils
#
# MIT License: (C) 2020 Dídac Coll


class TextUtils:
    """This class helps to create bold, italics and change color text.

    """

    @staticmethod
    def bold(text):
        """Bold text converter.

        :param text: a text string.
        :type text: str
        :return: a string like this example: ``'**text**'``
        :rtype: str"""
        return '**' + text + '**'

    @staticmethod
    def italics(text):
        """Italics text converter.

        :param text: a text string.
        :type text: str
        :return: a string like this example: ``'_text_'``
        :rtype: str"""
        return '*' + text + '*'

    @staticmethod
    def inline_code(text):
        """Inline code text converter.

        :param text: a text string.
        :type text: str
        :return: a string like this example: ``'``text``'``
        :rtype: str"""
        return '``' + text + '``'

    @staticmethod
    def center_text(text):
        """Place a text string to center.

        :param text: a text string.
        :type text: str
        :return: a string like this exampple: ``'<center>text</center>'``
        """
        return '<center>' + text + '</center>'

    @staticmethod
    def text_color(text, color="black"):
        """Change text color.

        :param text: it is the text that will be changed its color.
        :param color: it is the text color: ``'orange'``, ``'blue'``, ``'red'``...
                      or a **RGB** color such as ``'#ffce00'``.
        :return: a string like this one: ``'<font color='color'>'text'</font>'``
        :type text: str
        :type color: str
        :rtype: str
        """
        return '<font color="' + color + '">' + text + '</font>'

    @staticmethod
    def text_external_link(text, link=''):
        """ Using this method can be created an external link of a file or a web page.

        :param text: Text to be displayed.
        :type text: str
        :param link: External Link.
        :type link: str
        :return: return a string like this: ``'[Text to be shown](https://write.link.com)'``
        :rtype: str"""

        return '[' + text + '](' + link + ')'

    @staticmethod
    def insert_code(code, language=''):
        """This method allows to insert a peace of code.

        :param code: code string.
        :type code:str
        :param language: code language: python. c++, c#...
        :type language: str
        :return: markdown style.
        :rtype: str
        """
        if language == '':
            return '```\n' + code + '\n```'
        else:
            return '```' + language + '\n' + code + '\n```'

    @staticmethod
    def text_format(text, bold_italics_code='', color='black', align=''):
        """Text format helps to write multiple text format such as bold, italics and color.

        :param text: it is a string in which will be added the mew format
        :param bold_italics_code: using `'b'`: **bold**, `'i'`: _italics_ and `'c'`: `inline_code`.
        :param color: Can change text color. For example: 'red', 'green, 'orange'...
        :param align: Using this parameter you can align text.
        :return: return a string with the new text format.
        :type text: str
        :type bold_italics_code: str
        :type color: str
        :type align: str
        :rtype: str

        :Example:

        >>> from mdutils.tools.TextUtils import TextUtils
        >>> TextUtils.text_format(text='Some Text Here', bold_italics_code='bi', color='red', align='center')
        '***<center><font color="red">Some Text Here</font></center>***'
        """
        new_text_format = text
        if bold_italics_code:
            if ('c' in bold_italics_code) or ('b' in bold_italics_code) or ('i' in bold_italics_code):
                if 'c' in bold_italics_code:
                    new_text_format = TextUtils.inline_code(new_text_format)
            else:
                raise ValueError("unexpected bold_italics_code value, options available: 'b', 'c' or 'i'.")

        if color != 'black':
            new_text_format = TextUtils.text_color(new_text_format, color)

        if align == 'center':
            new_text_format = TextUtils.center_text(new_text_format)

        if bold_italics_code:
            if ('c' in bold_italics_code) or ('b' in bold_italics_code) or ('i' in bold_italics_code):
                if 'b' in bold_italics_code:
                    new_text_format = TextUtils.bold(new_text_format)
                if 'i' in bold_italics_code:
                    new_text_format = TextUtils.italics(new_text_format)
            else:
                raise ValueError("unexpected bold_italics_code value, options available: 'b', 'c' or 'i'.")

        return new_text_format

    @staticmethod
    def add_tooltip(link, tip):
        """
        :param link:
        :type link: str
        :param tip:
        :type tip: str
        return: ``link + "'" + format + "'"``
        """
        return link + " '{}'".format(tip)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
