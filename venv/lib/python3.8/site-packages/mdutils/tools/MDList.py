# Python
#
# This module implements tests for Header class.
#
# This file is part of mdutils. https://github.com/didix21/mdutils
#
# MIT License: (C) 2020 Dídac Coll
import re


class MDListHelper:
    def __init__(self):
        self.n_tabs = 0

    def _get_unordered_markdown_list(self, items: [str], marker: str) -> str:
        md_list = ""
        for item in items:
            if isinstance(item, list):
                self.n_tabs += 1
                md_list += self._get_unordered_markdown_list(item, marker)
                self.n_tabs -= 1
            else:
                md_list += self._add_new_item(item, marker)

        return md_list

    def _get_ordered_markdown_list(self, items: [str]) -> str:
        md_list = ""
        n_marker = 1
        for item in items:
            if isinstance(item, list):
                self.n_tabs += 1
                md_list += self._get_ordered_markdown_list(items=item)
                self.n_tabs -= 1
            else:
                md_list += self._add_new_item(item, f"{n_marker}.")
                n_marker += 1
        return md_list

    def _add_new_item(self, item: str, marker: str):
        item_with_hyphen = item if self._is_there_marker_in_item(item) else self._add_hyphen(item, marker)
        return self._n_spaces(4 * self.n_tabs) + item_with_hyphen + '\n'

    @classmethod
    def _is_there_marker_in_item(cls, item: str) -> bool:
        if item.startswith('-') or item.startswith('*') or item.startswith('+') or re.search(r"^(\d\.)", item):
            return True
        return False

    @classmethod
    def _add_hyphen(cls, item: str, marker: str):
        return f"{marker} {item}"

    @classmethod
    def _n_spaces(cls, number_spaces: int = 1):
        return " " * number_spaces


class MDList(MDListHelper):
    """This class allows to create unordered or ordered MarkDown list.

    """
    def __init__(self, items: [str], marked_with: str = '-'):
        """

        :param items: Array of items for generating the list.
        :type items: [str]
        :param marked_with: By default has the value of ``'-'``, can be ``'+'``, ``'*'``. If you want to generate
         an ordered list then set to ``'1'``.
        :type marked_with: str
        """
        super().__init__()
        self.md_list = self._get_ordered_markdown_list(items) if marked_with == '1' else \
            self._get_unordered_markdown_list(items, marked_with)

    def get_md(self) -> str:
        """Get the list in markdown format.

        :return:
        :rtype: str
        """
        return self.md_list


class MDCheckbox(MDListHelper):
    """This class allows to create checkbox MarkDown list.

    """

    def __init__(self, items: [str], checked: bool = False):
        """

        :param items: Array of items for generating the list.
        :type items: [str]
        :param checked: Set to ``True``, if you want that all items become checked. By default is set to ``False``.
        :type checked: bool
        """
        super().__init__()
        self.checked = " " if not checked else 'x'
        self.md_list = self._get_unordered_markdown_list(items, marker=f'- [{self.checked}]')

    def get_md(self) -> str:
        return self.md_list

    def _add_new_item(self, item: str, marker: str):
        item_with_hyphen = self._add_hyphen(item[2:], '- [x]') if self.__is_checked(item) \
            else self._add_hyphen(item, marker)
        return self._n_spaces(4 * self.n_tabs) + item_with_hyphen + '\n'

    @classmethod
    def __is_checked(cls, item: str) -> bool:
        return item.startswith('x')
