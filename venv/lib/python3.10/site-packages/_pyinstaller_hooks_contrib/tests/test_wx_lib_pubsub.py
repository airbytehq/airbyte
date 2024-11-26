#-----------------------------------------------------------------------------
# Copyright (c) 2005-2023, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------

from PyInstaller.utils.tests import importorskip


@importorskip('wx.lib.pubsub')
def test_wx_lib_pubsub_protocol_default(pyi_builder):
    pyi_builder.test_source(
        """
        from wx.lib.pubsub import pub

        def on_message(number):
            print('Message received.')
            if not number == 762:
                raise SystemExit('Message data "762" expected but received "%s".' % str(number))

        pub.subscribe(on_message, 'topic.subtopic')
        pub.sendMessage('topic.subtopic', number=762)
        """)


# Functional test exercising the non-default protocol `arg1` of version 3 of the PyPubSub API.
@importorskip('wx.lib.pubsub.core')
def test_wx_lib_pubsub_protocol_kwargs(pyi_builder):
    pyi_builder.test_source(
        """
        from wx.lib.pubsub import setuparg1  # noqa: F401
        from wx.lib.pubsub import pub

        def on_message(message):
            print('Message received.')
            if not message.data == 762:
                raise SystemExit('Message data "762" expected but received "%s".' % str(message.data))

        pub.subscribe(on_message, 'topic.subtopic')
        pub.sendMessage('topic.subtopic', 762)
        """)


# Functional test exercising the default protocol `kwargs` of version 3 of the PyPubSub API.
@importorskip('wx.lib.pubsub.core')
def test_wx_lib_pubsub_protocol_arg1(pyi_builder):
    pyi_builder.test_source(
        """
        from wx.lib.pubsub import setupkwargs  # noqa: F401
        from wx.lib.pubsub import pub

        def on_message(number):
            print('Message received.')
            if not number == 762:
                raise SystemExit('Message data "762" expected but received "%s".' % str(number))

        pub.subscribe(on_message, 'topic.subtopic')
        pub.sendMessage('topic.subtopic', number=762)
        """)
