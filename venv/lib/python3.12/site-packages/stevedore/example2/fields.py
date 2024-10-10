# -*- coding: utf-8 -*-
# Copyright (C) 2020 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import textwrap

from stevedore.example import base


class FieldList(base.FormatterBase):
    """Format values as a reStructuredText field list.

    For example::

      : name1 : value
      : name2 : value
      : name3 : a long value
          will be wrapped with
          a hanging indent
    """

    def format(self, data):
        """Format the data and return unicode text.

        :param data: A dictionary with string keys and simple types as
                     values.
        :type data: dict(str:?)
        """
        for name, value in sorted(data.items()):
            full_text = ': {name} : {value}'.format(
                name=name,
                value=value,
            )
            wrapped_text = textwrap.fill(
                full_text,
                initial_indent='',
                subsequent_indent='    ',
                width=self.max_width,
            )
            yield wrapped_text + '\n'
