# Python
#
# This module implements a text class that allows to modify and create text on Markdown files.
#
# This file is part of mdutils. https://github.com/didix21/mdutils
#
# MIT License: (C) 2020 Dídac Coll

from mdutils.tools.Link import Inline, Reference


class Image:

    def __init__(self, reference):
        """
        :param reference:
        :type reference: Reference
        """
        self.reference = reference

    @staticmethod
    def new_inline_image(text, path, tooltip=None):
        """
        :param text: Text that is going to be displayed in the markdown file as a iamge.
        :type text: str
        :param path: Image's path / link.
        :type path: str
        :param tooltip:
        :type tooltip: str
        :return: return the image in markdown format ``'![ + text + '](' + path + 'tooltip' + ')'``.
        :rtype: str
        """
        return '!' + Inline.new_link(link=path, text=text, tooltip=tooltip)

    def new_reference_image(self, text, path, reference_tag=None, tooltip=None):
        """
        :param text: Text that is going to be displayed in the markdown file as a image.
        :type text: str
        :param path: Image's path / link.
        :type path: str
        :param reference_tag: Tag that will be placed at the end of the markdown file jointly with the image's path.
        :type reference_tag: str
        :param tooltip:
        :type tooltip: str
        :return: return the image in markdown format ``'![ + text + '][' + reference_tag + ']'``.
        :rtype: str
        """
        return '!' + self.reference.new_link(link=path, text=text, reference_tag=reference_tag, tooltip=tooltip)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
