"""
# 🖋 editor - Open a text editor 🖋

`editor` opens the default text editor or your favorite editor to edit an existing file,
a new file, or a tempfile, blocks while the user edits text, then returns the contents
of the file.

You can pass a parameter `editor=` to specify an editor or leave it empty, in which
case the editor is:

* The contents of the environment variable `VISUAL`, if it's set, otherwise:
* The the contents of the environment variable `EDITOR`, if it's set, otherwise:
* The string `'Notepad'`, if the code is running on Windows, otherwise:
* The string `'vim'`

### Example 1: Using a temporary file

If no filename is provided, a temporary file gets edited, and its contents
returned.

    import editor

    comments = editor.editor(text='Comments here\\n\\n')
    # Pop up the default editor with a tempfile containing "Comments here",
    # then return the contents and delete the tempfile.

### Example 2: Using a named file

If a filename is provided, then that file gets edited.

    import os

    FILE = 'file.txt'
    assert not os.path.exists(FILE)

    comments = editor.editor(text=MESSAGE, filename=FILE)
    # Pop up an editor for a new FILE containing MESSAGE, user edits
    # This file is saved when the user exits the editor.

    assert os.path.exists(FILE)

    # You can edit an existing file too, and select your own editor.
    comments2 = editor.editor(filename=FILE, editor='emacs -nw')
"""

import os
import platform
import tempfile
import traceback
import typing as t
from pathlib import Path

import runs
import xmod

__all__ = 'editor', 'default_editor'

DEFAULT_EDITOR = 'vim'
EDITORS = {'Windows': 'notepad'}


@xmod.xmod(mutable=True)
def editor(
    text: t.Optional[str] = None,
    filename: t.Union[None, Path, str] = None,
    editor: t.Optional[str] = None,
    **kwargs: t.Mapping,
) -> str:
    """
    Open a text editor, block while the user edits, then return the results

    Args:

      text: A string which is written to the file before the editor is opened.
          If `None`, the file is left unchanged.

      filename: The name of the file to edit.
          If `None`, a temporary file is used.

      editor: A string containing the command used to invoke the text editor.
         If `None`, use `editor.default_editor()`.

      kwargs: Arguments passed on to `subprocess.call()`"""
    editor = editor or default_editor()
    is_temp = not filename
    if filename is not None:
        fname = filename
    else:
        fd, fname = tempfile.mkstemp()
        os.close(fd)

    try:
        path = Path(fname)
        if text is not None:
            path.write_text(text)

        cmd = '{} "{}"'.format(editor, path.resolve())
        runs.call(cmd, **kwargs)
        return path.read_text()

    finally:
        if is_temp:
            try:
                path.unlink()
            except Exception:
                traceback.print_exc()


def default_editor() -> str:
    """
    Return the default text editor.

    The default text editor is the contents of the environment variable
    `EDITOR`, it it's non-empty, otherwise if the platform is Windows, it's
    `'notepad'`, otherwise `'vim'`.
    """
    return os.environ.get('VISUAL') or (
        os.environ.get('EDITOR')
        or EDITORS.get(platform.system(), DEFAULT_EDITOR)
    )
