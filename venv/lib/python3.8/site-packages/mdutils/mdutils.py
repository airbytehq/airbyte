# Python
#
# This module implements the Main Markdown class.
#
# This file is part of mdutils. https://github.com/didix21/mdutils
#
# MIT License: (C) 2018 Dídac Coll

"""Module **mdutils**

The available features are:
    * Create Headers, Til 6 sub-levels.
    * Auto generate a table of contents.
    * Create List and sub-list.
    * Create paragraph.
    * Generate tables of different sizes.
    * Insert Links.
    * Insert Code.
    * Place text anywhere using a marker.
"""
import mdutils.tools.Table
import mdutils.tools.TableOfContents
from mdutils.fileutils.fileutils import MarkDownFile
from mdutils.tools.Header import Header
from mdutils.tools.Image import Image
from mdutils.tools.Link import Inline, Reference
from mdutils.tools.TextUtils import TextUtils
from mdutils.tools.MDList import MDList, MDCheckbox
from textwrap import fill


class MdUtils:
    """This class give some basic methods that helps the creation of Markdown files while you are executing a python
    code.

    The ``__init__`` variables are:

    - **file_name:** it is the name of the Markdown file.
    - **author:** it is the author fo the Markdown file.
    - **header:** it is an instance of Header Class.
    - **textUtils:** it is an instance of TextUtils Class.
    - **title:** it is the title of the Markdown file. It is written with Setext-style.
    - **table_of_contents:** it is the table of contents, it can be optionally created.
    - **file_data_text:** contains all the file data that will be written on the markdown file.
    """

    def __init__(self, file_name, title="", author=""):
        """

        :param file_name: it is the name of the Markdown file.
        :type file_name: str
        :param title: it is the title of the Markdown file. It is written with Setext-style.
        :type title: str
        :param author: it is the author fo the Markdown file.
        :type author: str
        """
        self.file_name = file_name
        self.author = author
        self.header = Header()
        self.textUtils = TextUtils
        self.title = self.header.choose_header(level=1, title=title, style='setext')
        self.table_of_contents = ""
        self.file_data_text = ""
        self._table_titles = []
        self.reference = Reference()
        self.image = Image(reference=self.reference)

    def create_md_file(self):
        """It creates a new Markdown file.
        :return: return an instance of a MarkDownFile."""
        md_file = MarkDownFile(self.file_name)
        md_file.rewrite_all_file(
            data=self.title + self.table_of_contents + self.file_data_text + self.reference.get_references_as_markdown()
        )
        return md_file

    def read_md_file(self, file_name):
        """Reads a Markdown file and save it to global class `file_data_text`.

        :param file_name: Markdown file's name that has to be read.
        :type file_name: str
        :return: optionally returns the file data content.
        :rtype: str
        """
        file_data = MarkDownFile().read_file(file_name)
        self.___update_file_data(file_data)

        return file_data

    def new_header(self, level, title, style='atx', add_table_of_contents='y'):
        """Add a new header to the Markdown file.

        :param level: Header level. *atx* style can take values 1 til 6 and *setext* style take values 1 and 2.
        :type level: int
        :param title: Header title.
        :type title: str
        :param style: Header style, can be ``'atx'`` or ``'setext'``. By default ``'atx'`` style is chosen.
        :type style: str
        :param add_table_of_contents: by default the atx and setext headers of level 1 and 2 are added to the \
        table of contents, setting this parameter to 'n'.
        :type add_table_of_contents: str

        :Example:
        >>> from mdutils import MdUtils
        >>> mdfile = MdUtils("Header_Example")
        >>> print(mdfile.new_header(level=2, title='Header Level 2 Title', style='atx', add_table_of_contents='y'))
        '\\n## Header Level 2 Title\\n'
        >>> print(mdfile.new_header(level=2, title='Header Title', style='setext'))
        '\\nHeader Title\\n-------------\\n'

        """
        if add_table_of_contents == 'y':
            self.__add_new_item_table_of_content(level, title)
        self.___update_file_data(self.header.choose_header(level, title, style))
        return self.header.choose_header(level, title, style)

    def __add_new_item_table_of_content(self, level, item):
        """Automatically add new atx headers to the table of contents.

        :param level: add levels up to 6.
        :type level: int
        :param item: items to add.
        :type item: list or str

        """

        curr = self._table_titles

        for i in range(level-1):
            curr = curr[-1]

        curr.append(item)

        if level < 6:
            curr.append([])


    def new_table_of_contents(self, table_title="Table of contents", depth=1, marker=''):
        """Table of contents can be created if Headers of 'atx' style have been defined.

        This method allows to create a table of contents and define a title for it. Moreover, `depth` allows user to
        define how many levels of headers will be placed in the table of contents.
        If no marker is defined, the table of contents will be placed automatically after the file's title.

        :param table_title: The table content's title, by default "Table of contents"
        :type table_title: str
        :param depth: allows to include atx headers 1 through 6. Possible values: 1, 2, 3, 4, 5, or 6.
        :type depth: int
        :param marker: allows to place the table of contents using a marker.
        :type marker: str
        :return: a string with the data is returned.
        :rtype: str

        """

        if marker:
            self.table_of_contents = ""
            marker_table_of_contents = self.header.choose_header(level=1, title=table_title, style='setext')
            marker_table_of_contents += mdutils.tools.TableOfContents.TableOfContents().create_table_of_contents(
                self._table_titles, depth)
            self.file_data_text = self.place_text_using_marker(marker_table_of_contents, marker)
        else:
            marker_table_of_contents = ""
            self.table_of_contents += self.header.choose_header(level=1, title=table_title, style='setext')
            self.table_of_contents += mdutils.tools.TableOfContents.TableOfContents().create_table_of_contents(
                self._table_titles, depth)

        return self.table_of_contents + marker_table_of_contents

    def new_table(self, columns, rows, text, text_align='center', marker=''):
        """This method takes a list of strings and creates a table.

            Using arguments ``columns`` and ``rows`` allows to create a table of *n* columns and *m* rows. The
            ``columns * rows`` operations has to correspond to the number of elements of ``text`` list argument.
            Moreover, ``argument`` allows to place the table wherever you want from the file.

        :param columns: this variable defines how many columns will have the table.
        :type columns: int
        :param rows: this variable defines how many rows will have the table.
        :type rows: int
        :param text: it is a list containing all the strings which will be placed in the table.
        :type text: list
        :param text_align: allows to align all the cells to the ``'right'``, ``'left'`` or ``'center'``.
                            By default: ``'center'``.
        :type text_align: str
        :param marker: using ``create_marker`` method can place the table anywhere of the markdown file.
        :type marker: str
        :return: can return the table created as a string.
        :rtype: str

        :Example:
        >>> from mdutils import MdUtils
        >>> md = MdUtils(file_name='Example')
        >>> text_list = ['List of Items', 'Description', 'Result', 'Item 1', 'Description of item 1', '10', 'Item 2', 'Description of item 2', '0']
        >>> table = md.new_table(columns=3, rows=3, text=text_list, text_align='center')
        >>> print(repr(table))
        '\\n|List of Items|Description|Result|\\n| :---: | :---: | :---: |\\n|Item 1|Description of item 1|10|\\n|Item 2|Description of item 2|0|\\n'


            .. csv-table:: **Table result on Markdown**
               :header: "List of Items", "Description", "Results"

               "Item 1", "Description of Item 1", 10
               "Item 2", "Description of Item 2", 0

        """

        new_table = mdutils.tools.Table.Table()
        text_table = new_table.create_table(columns, rows, text, text_align)
        if marker:
            self.file_data_text = self.place_text_using_marker(text_table, marker)
        else:
            self.___update_file_data(text_table)

        return text_table

    def new_paragraph(self, text='', bold_italics_code='', color='black', align='', wrap_width=120):
        """Add a new paragraph to Markdown file. The text is saved to the global variable file_data_text.

        :param text: is a string containing the paragraph text. Optionally, the paragraph text is returned.
        :type text: str
        :param bold_italics_code: using ``'b'``: **bold**, ``'i'``: *italics* and ``'c'``: ``inline_code``.
        :type bold_italics_code: str
        :param color: Can change text color. For example: ``'red'``, ``'green'``, ``'orange'``...
        :type color: str
        :param align: Using this parameter you can align text.
        :type align: str
        :param wrap_width: wraps text with designated width by number of characters. By default, long words are not broken. 
                           Use width of 0 to disable wrapping.
        :type wrap_width: int
        :return:  ``'\\n\\n' + text``. Not necessary to take it, if only has to be written to
                    the file.
        :rtype: str

        """

        if wrap_width > 0:
            text = fill(text, wrap_width, break_long_words=False, replace_whitespace=False, drop_whitespace=False)

        if bold_italics_code or color != 'black' or align:
            self.___update_file_data('\n\n' + self.textUtils.text_format(text, bold_italics_code, color, align))
        else:
            self.___update_file_data('\n\n' + text)

        return self.file_data_text

    def new_line(self, text='', bold_italics_code='', color='black', align='', wrap_width=120):
        """Add a new line to Markdown file. The text is saved to the global variable file_data_text.

        :param text: is a string containing the paragraph text. Optionally, the paragraph text is returned.
        :type text: str
        :param bold_italics_code: using ``'b'``: **bold**, ``'i'``: *italics* and ``'c'``: ``inline_code``...
        :type bold_italics_code: str
        :param color: Can change text color. For example: ``'red'``, ``'green'``, ``'orange'``...
        :type color: str
        :param align: Using this parameter you can align text. For example ``'right'``, ``'left'`` or ``'center'``.
        :type align: str
        :param wrap_width: wraps text with designated width by number of characters. By default, long words are not broken. 
                           Use width of 0 to disable wrapping.
        :type wrap_width: int
        :return: return a string ``'\\n' + text``. Not necessary to take it, if only has to be written to the
                    file.
        :rtype: str
        """

        if wrap_width > 0:
            text = fill(text, wrap_width, break_long_words=False, replace_whitespace=False, drop_whitespace=False)

        if bold_italics_code or color != 'black' or align:
            self.___update_file_data('  \n' + self.textUtils.text_format(text, bold_italics_code, color, align))
        else:
            self.___update_file_data('  \n' + text)

        return self.file_data_text

    def write(self, text='', bold_italics_code='', color='black', align='', marker='', wrap_width=120):
        """Write text in ``file_Data_text`` string.

        :param text: a text a string.
        :type text: str
        :param bold_italics_code: using ``'b'``: **bold**, ``'i'``: *italics* and ``'c'``: ``inline_code``...
        :type bold_italics_code: str
        :param color: Can change text color. For example: ``'red'``, ``'green'``, ``'orange'``...
        :type color: str
        :param align: Using this parameter you can align text. For example ``'right'``, ``'left'`` or ``'center'``.
        :type align: str
        :param wrap_width: wraps text with designated width by number of characters. By default, long words are not broken. 
                           Use width of 0 to disable wrapping.
        :type wrap_width: int
        :param marker: allows to replace a marker on some point of the file by the text.
        :type marker: str
        """

        if wrap_width > 0:
            text = fill(text, wrap_width, break_long_words=False, replace_whitespace=False, drop_whitespace=False)

        if bold_italics_code or color or align:
            new_text = self.textUtils.text_format(text, bold_italics_code, color, align)
        else:
            new_text = text

        if marker:
            self.file_data_text = self.place_text_using_marker(new_text, marker)
        else:
            self.___update_file_data(new_text)

        return new_text

    def insert_code(self, code, language=''):
        """This method allows to insert a peace of code on a markdown file.

        :param code: code string.
        :type code: str
        :param language: code language: python, c++, c#...
        :type language: str
        :return:
        :rtype: str
        """
        md_code = '\n\n' + self.textUtils.insert_code(code, language)
        self.___update_file_data(md_code)
        return md_code

    def create_marker(self, text_marker):
        """This will add a marker to ``file_data_text`` and returns the marker result in order to be used whenever
            you need.

            Markers allows to place them to the string data text and they can be replaced by a peace of text using
            ``place_text_using_marker`` method.

        :param text_marker: marker name.
        :type text_marker: str
        :return: return a marker of the following form: ``'##--[' + text_marker + ']--##'``
        :rtype: str
        """

        new_marker = '##--[' + text_marker + ']--##'
        self.___update_file_data(new_marker)
        return new_marker

    def place_text_using_marker(self, text, marker):
        """It replace a previous marker created with ``create_marker`` with a text string.

            This method is going to search for the ``marker`` argument, which has been created previously using
            ``create_marker`` method, in ``file_data_text`` string.

        :param text: the new string that will replace the marker.
        :type text: str
        :param marker: the marker that has to be replaced.
        :type marker: str
        :return: return a new file_data_text with the replace marker.
        :rtype: str
        """
        return self.file_data_text.replace(marker, text)

    def ___update_file_data(self, file_data):
        self.file_data_text += file_data

    def new_inline_link(self, link, text=None, bold_italics_code='', align=''):
        """Creates a inline link in markdown format.

        :param link:
        :type link: str
        :param text: Text that is going to be displayed in the markdown file as a link.
        :type text: str
        :param bold_italics_code: Using ``'b'``: **bold**, ``'i'``: *italics* and ``'c'``: ``inline_code``...
        :type bold_italics_code: str
        :param align: Using this parameter you can align text. For example ``'right'``, ``'left'`` or ``'center'``.
        :type align: str
        :return: returns the link in markdown format ``'[ + text + '](' + link + ')'``. If text is not defined returns \
        ``'<' + link + '>'``.
        :rtype: str

        .. note::
            If param text is not provided, link param will be used instead.

        """
        if text is None:
            n_text = link
        else:
            n_text = text

        if bold_italics_code or align:
            n_text = self.textUtils.text_format(text=n_text, bold_italics_code=bold_italics_code, align=align)

        return Inline.new_link(link=link, text=n_text)

    def new_reference_link(self, link, text, reference_tag=None, bold_italics_code='', align=''):
        """Creates a reference link in markdown format. All references will be stored at the end of the markdown file.


        :param link:
        :type link: str
        :param text: Text that is going to be displayed in the markdown file as a link.
        :type text: str
        :param reference_tag: Tag that will be placed at the end of the markdown file jointly with the link.
        :type reference_tag: str
        :param bold_italics_code: Using ``'b'``: **bold**, ``'i'``: *italics* and ``'c'``: ``inline_code``...
        :type bold_italics_code: str
        :param align: Using this parameter you can align text. For example ``'right'``, ``'left'`` or ``'center'``.
        :type align: str
        :return: returns the link in markdown format ``'[ + text + '][' + link + ]'``.
        :rtype: str

        .. note::
            If param reference_tag is not provided, text param will be used instead.

        :Example:
        >>> from mdutils import MdUtils
        >>> md = MdUtils("Reference link")
        >>> link = md.new_reference_link(link='https://github.com', text='github', reference_tag='git')
        >>> md.new_link(link)
        >>> print(repr(link))
        '[github][git]'
        >>> link = md.new_reference_link(link='https://github.com/didix21/mdutils', text='mdutils')
        >>> md.new_link(link)
        >>> print(repr(link))
        '[mdutils]'
        >>> link = md.new_line(md.new_reference_link(link='https://github.com/didix21/mdutils', text='mdutils', reference_tag='md', bold_italics_code='b'))
        >>> md.new_link(link)
        >>> print(repr(link))
        '[**mdutils**][md]'
        >>> md.create_md_file()

        """

        if reference_tag is None:
            if bold_italics_code != '':
                raise TypeError('For using bold_italics_code param, reference_tag must be defined')
            if align != '':
                raise TypeError('For using align, reference_tag must be defined')

        n_text = text
        if bold_italics_code or align:
            n_text = self.textUtils.text_format(text=n_text, bold_italics_code=bold_italics_code, align=align)

        return self.reference.new_link(link=link, text=n_text, reference_tag=reference_tag)

    @staticmethod
    def new_inline_image(text, path):
        """Add inline images in a markdown file. For example ``[MyImage](../MyImage.jpg)``.

        :param text: Text that is going to be displayed in the markdown file as a iamge.
        :type text: str
        :param path: Image's path / link.
        :type path: str
        :return: return the image in markdown format ``'![ + text + '](' + path + ')'``.
        :rtype: str

        """

        return Image.new_inline_image(text=text, path=path)

    def new_reference_image(self, text, path, reference_tag=None):
        """Add reference images in a markdown file. For example ``[MyImage][my_image]``. All references will be stored
        at the end of the markdown file.

        :param text: Text that is going to be displayed in the markdown file as a image.
        :type text: str
        :param path: Image's path / link.
        :type path: str
        :param reference_tag: Tag that will be placed at the end of the markdown file jointly with the image's path.
        :type reference_tag: str
        :return: return the image in markdown format ``'![ + text + '][' + reference_tag + ']'``.
        :rtype: str

        .. note::
            If param reference_tag is not provided, text param will be used instead.
        """
        return self.image.new_reference_image(text=text, path=path, reference_tag=reference_tag)

    def new_list(self, items: [str], marked_with: str = "-"):
        """Add unordered or ordered list in MarkDown file.

        :param items: Array of items for generating the list.
        :type items: [str]
        :param marked_with: By default has the value of ``'-'``, can be ``'+'``, ``'*'``. If you want to generate
         an ordered list then set to ``'1'``.
        :type marked_with: str
        :return:
        """
        mdlist = MDList(items, marked_with)
        self.___update_file_data('\n' + mdlist.get_md())

    def new_checkbox_list(self, items: [str], checked: bool = False):
        """Add checkbox list in MarkDown file.

        :param items: Array of items for generating the checkbox list.
        :type items: [str]
        :param checked: if you set this to ``True``. All checkbox will be checked. By default is ``False``.
        :type checked: bool
        :return:
        """

        mdcheckbox = MDCheckbox(items=items, checked=checked)
        self.___update_file_data('\n' + mdcheckbox.get_md())


if __name__ == "__main__":
    import doctest

    doctest.testmod()
