# Python
#
# This module implements a text class that allows to modify and create text on Markdown files.
#
# This file is part of mdutils. https://github.com/didix21/mdutils
#
# MIT License: (C) 2020 Dídac Coll
import re


class TableOfContents:
    def _loop_through(self, elements, tab='', depth=1):
        """Method that go through a list of elements that contain strings and other list and return a string.

        The returned string is ready to be written in a markdown file in order to create a table of contents.

        :param elements: contain all the headers defined on the main class.
        :param tab: Inserts tabulations.
        :param depth: allows to include atx headers 1 through 6. Possible values: 1, 2, 3, 4, 5, or 6.
        :type elements: list
        :type tab: str
        :type depth: int
        :rtype: str
        """
        elements_to_string = ""
        for item in elements:
            if isinstance(item, list):
                if item and depth > 1:
                    elements_to_string += self._loop_through(item, tab=tab+'\t', depth=depth-1)
            else:
                elements_to_string += '\n' + tab + '* [' + item + '](#' \
                                      + re.sub('[^a-z0-9_\-]', '', item.lower().replace(' ', '-')) + ')'

        return elements_to_string

    def create_table_of_contents(self, array_of_title_contents, depth=1):
        """This method can create a table of contents using an array of the different titles. The depth can be changed.
        :param array_of_title_contents: a string list with the different headers.
        :type array_of_title_contents: list
        :param depth: allows to include atx headers 1 through 6. Possible values: 1, 2, 3, 4, 5, or 6.
        :type depth: int
        :return: return a string ready to be written to a Markdown file.
        :rtype: str
        """
        if depth in range(1,7):
            table_of_contents = ""
            table_of_contents += self._loop_through(array_of_title_contents, depth=depth)
            table_of_contents += '\n'
            return table_of_contents
        else:
            raise ValueError("depth's expected value: between 1 and 6, but depth = " + str(depth))


if __name__ == "__main__":
    import doctest

    doctest.testmod()
