# Python
#
# This module implements a text class that allows to modify and create text on Markdown files.
#
# This file is part of mdutils. https://github.com/didix21/mdutils
#
# MIT License: (C) 2020 Dídac Coll
from typing import Optional, Union, Iterable


class Table:

    def __init__(self):
        self.rows = 0
        self.columns = 0

    @staticmethod
    def _align(columns: int, text_align: Optional[Union[str, Iterable]] = None) -> str:
        """ This private method it's in charge of aligning text of a table.

        - notes: more information about `text_align`

        :param columns: it is the number of columns.
        :param text_align: it is a string giving information about the alignment that is wanted.  text_align can take
                           the following parameters: ``'center'``, ``'right'`` and ``'left'``.
        :return: returns a string of type ``'| :---: | :---: | :---: |'``.
        :type columns: int
        :type text_align: str
        :rtype: str

        .. note:
        """

        column_align_string = ''
        ta2pat={ # text_align to pattern translator
            'center': ' :---: |',
            'left': ' :--- |',
            'right': ' ---: |',
            None: ' --- |'
        }
        if type(text_align) == str:
            
            text_align = [text_align.lower()]*columns
            
        elif text_align is None:
            
            text_align = [None]*columns
            
        else:
            
            text_align = list(text_align)[:columns] # make a local redimensionnable copy
        
        if len(text_align) < columns:
            
            text_align += [None]*(columns-len(text_align))
            
        column_align_string = '|'
        for i,ta in enumerate(text_align):
            
            if not ta is None:
                
                ta = ta.lower()
                
            if ta not in ta2pat:
                
                raise ValueError(f"text_align's expected value: 'right', 'center', 'left' or None , but in column {i+1} text_align = '{ta}'")
            
            column_align_string += ta2pat[ta]

        return column_align_string

    def create_table(self, columns: int, rows: int, text: [str], text_align: Optional[Union[str, list]] = None):
        """This method takes a list of strings and creates a table.

            Using arguments ``columns`` and ``rows`` allows to create a table of *n* columns and *m* rows.
            The ``columns * rows`` operations has to correspond to the number of elements of ``text`` list argument.

        :param int columns: number of columns of the table.
        :param int rows: number of rows of the table.
        :param text: a list of strings.
        :type text: list of str
        :param str_or_list text_align: text align argument. Values available are: ``'right'``, ``'center'``, ``'left'`` and ``None`` (default). If text_align is a list then individual alignment can be set for each column.
        :return: a markdown table.
        :rtype: str


        :Example:
        >>> from mdutils.tools.Table import Table
        >>> text_list = ['List of Items', 'Description', 'Result', 'Item 1', 'Description of item 1', '10', 'Item 2', 'Description of item 2', '0']
        >>> table = Table().create_table(columns=3, rows=3, text=text_list, text_align='center')
        >>> print(repr(table))
        '\\n|List of Items|Description|Result|\\n| :---: | :---: | :---: |\\n|Item 1|Description of item 1|10|\\n|Item 2|Description of item 2|0|\\n'


            .. csv-table:: **Table result on Markdown**
               :header: "List of Items", "Description", "Results"

               "Item 1", "Description of Item 1", 10
               "Item 2", "Description of Item 2", 0


        """
        self.columns = columns
        self.rows = rows
        table = '\n'
        column_align_string = self._align(columns, text_align)
        index = 0
        if columns * rows == len(text):
            for row in range(rows + 1):
                if row == 1:
                    table += column_align_string  # Row align, Example: '| :---: | :---: | ... | \n'
                else:
                    table += '|'
                    for _ in range(columns):
                        table += str(text[index]) + '|'
                        index += 1
                table += '\n'
            return table
        else:
            raise ValueError("columns * rows is not equal to text length")


if __name__ == "__main__":
    import doctest

    doctest.testmod()
