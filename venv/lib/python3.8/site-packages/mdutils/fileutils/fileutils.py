# Python
#
# This module implements a main class that allows to create markdown files, write in them or read.
#
# This file is part of mdutils. https://github.com/didix21/mdutils
#
# MIT License: (C) 2018 Dídac Coll


class MarkDownFile(object):
    """MarkDownFile class creates a new file of MarkDown extension.

    Features available are:
        - Create a file.
        - Rewrite a file with new data.
        - Write at the end of the file."""

    def __init__(self, name=''):
        """Creates a markdown file, if name is not empty.
        :param str name: file name"""
        if name:
            self.file_name = name if name.endswith('.md') else name + '.md'
            self.file = open(self.file_name, 'w+', encoding='UTF-8')
            self.file.close()

    def rewrite_all_file(self, data):
        """Rewrite all the data of a Markdown file by ``data``.

        :param str data: is a string containing all the data that is written in the markdown file."""
        with open(self.file_name, 'w', encoding='utf-8') as self.file:
            self.file.write(data)

    def append_end(self, data):
        """Write at the last position of a Markdown file.

        :param str data: is a string containing all the data that is written in the markdown file."""
        with open(self.file_name, 'a', encoding='utf-8') as self.file:
            self.file.write(data)

    def append_after_second_line(self, data):
        """Write after the file's first line.

        :param str data: is a string containing all the data that is written in the markdown file."""
        with open(self.file_name, 'r+', encoding='utf-8') as self.file:
            file_data = self.file.read()  # Save all the file's content
            self.file.seek(0, 0)  # Place file pointer at the beginning
            first_line = self.file.readline()  # Read the first line
            second_line = self.file.readline()  # Read the second line
            self.file.seek(len(first_line + second_line), 0)  # Place file pointer at the end of the first line
            self.file.write(data)  # Write data
            self.file.write('\n' + file_data[len(first_line + second_line):])

    @staticmethod
    def read_file(file_name):
        """Read a Markdown file using a file name. It is not necessary to add *.md extension.

        :param file_name: Markdown file's name.
        :type file_name: str
        :return: return all file's data.
        :rtype: str"""

        if file_name.find('.md') == -1:
            file_name += '.md'

        with open(file_name, 'r', encoding='utf-8') as file:
            file_data = file.read()

        return file_data


if __name__ == '__main__':
    new_file = MarkDownFile('Example')
    new_file.rewrite_all_file(data="# Some Text Example")
