# Python
#
# This module implements a text class that allows to modify and create text on Markdown files.
#
# This file is part of mdutils. https://github.com/didix21/mdutils
#
# MIT License: (C) 2020 Dídac Coll
from mdutils.tools.TextUtils import TextUtils


class Reference:

    def __init__(self):
        self.references = {}

    def get_references(self):
        """
        :return:
        :rtype: dict
        """
        return self.references

    def get_references_as_markdown(self):
        """
        :return:
        :rtype: str
        """
        if not bool(self.references):
            return ""

        references_as_markdown = ""
        for key in sorted(self.references.keys()):
            references_as_markdown += '[' + key + ']: ' + self.references[key] + '\n'
        return '\n\n\n' + references_as_markdown

    def new_link(self, link, text, reference_tag=None, tooltip=None):
        """
        :param link:
        :type link: str
        :param text: Text that is going to be displayed in the markdown file as a link.
        :type text: str
        :param reference_tag: Reference that will be saved on reference dict.
        :type reference_tag: str
        :param tooltip: Add a tooltip on the link.
        :type tooltip: str
        :return: ``'[' + text + '][' + reference_tag + ']'`` or if reference_Tag is not defined: ``'[' + text + ']'``.
        :rtype: str
        """
        if reference_tag is None:
            self.__update_ref(link, text, tooltip)
            return '[' + text + ']'

        self.__update_ref(link, reference_tag, tooltip)
        return '[' + text + '][' + reference_tag + ']'

    def __update_ref(self, link, reference_tag, tooltip=None):
        if not (reference_tag in self.references.keys()):
            if tooltip is not None:
                self.references.update({reference_tag: TextUtils.add_tooltip(link, tooltip)})
                return

            self.references.update({reference_tag: link})


class Inline:

    @staticmethod
    def new_link(link, text=None, tooltip=None):
        """
        :param link:
        :type link: str
        :param text: Text that is going to be displayed in the markdown file as a link.
        :type text: str
        :param tooltip: Add a tool tip on the image.
        :type tooltip: str
        :return: ``'[' + text +'](' + link + 'tooltip' + ')'`` or if link is only defined: ```<` + link '>'``.
        :rtype: str
        """

        if tooltip:
            if text is None:
                return Inline.__md_link(link=TextUtils.add_tooltip(link=link, tip=tooltip), text=link)

            return Inline.__md_link(link=TextUtils.add_tooltip(link=link, tip=tooltip), text=text)

        if text is None:
            return '<' + link + '>'

        return Inline.__md_link(link=link, text=text)

    @staticmethod
    def __md_link(link, text):
        return TextUtils.text_external_link(text, link)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
