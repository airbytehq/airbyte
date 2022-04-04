# Python
#
# This module implements a text class that allows to modify and create text on Markdown files.
#
# This file is part of mdutils. https://github.com/didix21/mdutils
#
# MIT License: (C) 2020 Dídac Coll


class Html:

    @staticmethod
    def paragraph(text: str, align: str = None) -> str:
        """
        :param text:
        :param align: ``center`` or ``right``.
        :type align: str
        :return: ``"<p align=\"{}\">\\n    {}\\n</p>".format(align, text)``.
        :rtype: str
        """

        if align is None:
            return '<p>\n    {}\n</p>'.format(text)

        if align is not None:
            if align not in ["left", "center", "right"]:
                raise KeyError

        return '<p align="{}">\n    {}\n</p>'.format(align, text)

    @classmethod
    def image(cls, path: str, size: str = None, align: str = None) -> str:
        """

        :param path:
        :type path: str
        :param size: (In px) for width write ``'<int>'``, for height write ``'x<int>'`` or \
        width and height ``'<int>x<int>``.
        :type size: str
        :param align: can be ``'left'``, ``'center'`` or ``'right'``.
        :type align: str
        :return: html format
        :rtype: str

        :Example:
        >>> Html.image(path='../image.jpg', size='200', align='center')
        >>> Html.image(path='../image.jpg', size='x200', align='left')
        >>> Html.image(path='../image.jpg', size='300x400')
        """

        if align:
            return cls.paragraph(text=cls.__html_image(path=path, size=size), align=align)

        return cls.__html_image(path=path, size=size)

    @classmethod
    def __html_image(cls, path: str, size: str = None):
        if size:
            return '<img src="{}" {}/>'.format(path, HtmlSize.size_to_width_and_height(size=size))
        return '<img src="{}" />'.format(path)


class HtmlSize:
    @classmethod
    def size_to_width_and_height(cls, size: str) -> str:
        size = cls.__pre_process_size(size=size)
        if size.isdigit():
            return cls.__get_width(size=size)

        if size.startswith('x'):
            height = size[1:]
            if height.isdigit():
                return cls.__get_height(size=height)

            raise SizeBadFormat(size)

        width_height = size.split('x')

        if len(width_height) == 2:
            if width_height[0].isdigit() and width_height[1].isdigit():
                return "{} {}".format(cls.__get_width(width_height[0]), cls.__get_height(width_height[1]))

        raise SizeBadFormat(size)

    @classmethod
    def __pre_process_size(cls, size: str) -> str:
        no_spaces = size.replace(" ", "")
        return no_spaces.lower()

    @classmethod
    def __get_width(cls, size: str) -> str:
        return 'width="{}"'.format(int(size))

    @classmethod
    def __get_height(cls, size: str):
        return 'height="{}"'.format(int(size))


class SizeBadFormat(Exception):
    """Raise exception when size does not match the expected format"""
    def __init__(self, message):
        Exception.__init__(self, "Unexpected format: {}. Expected: '<int>', 'x<int>' or '<int>x<int>'".format(message))
    pass
