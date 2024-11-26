"""
🏃 runs: a better subprocess 🏃
---------------------------------------------------------------------

`runs` has improved versions of `call()`, `check_call()`, `check_output()`,
and `run()` from Python's `subprocess` module that handle multiple commands and
blocks of text, fix some defects, and add some features.


    import runs

    runs('''
        ls
        df -k  # or perhaps -h?
        echo 'Done and done'
    ''')

---

`subprocess` is essential but:

* You can only run one command at a time

* Commands to subprocess must be either a sequence of strings or a string,
  depending on whether `shell=True` or not

* Results are returned by default as bytes and not strings

---

The `runs` functions let you run a block of text as a sequence of subprocess
calls.

`runs` provides call-compatible replacements for the functions
`subprocess.call()`, `subprocess.check_call()`, `subprocess.check_output()`,
and `subprocess.run()`

Each replacement function takes a block of text, which is split into individual
command lines, or a list of commands, and returns a list of values, one for
each command.  A block of text can contain line continuations, and comments,
which are ignored.

The replacement functions also add optional logging, error handling,
and lazy evaluation, and use UTF-8 encoding by default.

The module `runs` is callable - `runs()` is a synonym for `runs.run()`.

EXAMPLES:


    # `runs()` or `runs.run()` writes to stdout and stderr just as if you'd run
    # the commands from the terminal

    import runs

    runs('echo "hello, world!"')  # prints hello, world!

    # runs.check_output() returns a list, one string result for each command

    results = check_output('''
        echo  line   one  # Here's line one.
        echo   'line "  two  "'  # and two!
    ''')
    assert results == ['line one', 'line "  two  "']

    # Line continuations work too, either single or double
    runs('''
        ls -cail

        # One command that takes many lines.
        g++ -DDEBUG  -O0 -g -std=c++17 -pthread -I ./include -lm -lstdc++ \\
          -Wall -Wextra -Wno-strict-aliasing -Wpedantic \\\\
          -MMD -MP -MF -c src/tests.cpp -o build/./src/tests.cpp.o

        echo DONE
     ''')

NOTES:

Exactly like `subprocess`, `runs` differs from the shell in a few ways, so
you can't just paste your shell scripts in:

* Redirection doesn't work.


    result = runs.check_output('echo foo > bar.txt')
    assert result == ['foo > bar.txt\\n']

* Pipes don't work.


    result = runs.check_output('echo foo | wc')
    assert result == ['foo | wc \\n']

*  Environment variables are not expanded in command lines


    result = runs.check_output('echo $FOO', env={'FOO': 'bah!'})
    assert result == ['$FOO\\n']

Environment variables are exported to the subprocess, absolutely,
but no environment variable expension happens on command lines.
"""

import functools
import shlex
import subprocess
import sys

import xmod

__all__ = 'call', 'check_call', 'check_output', 'run', 'split_commands'


def _run(name, commands, *args, on_exception=None, echo=False, **kwargs):
    if echo is True:
        echo = '$'

    if echo == '':
        echo = print

    if echo and not callable(echo):
        echo = functools.partial(print, echo)

    if on_exception is True:
        on_exception = lambda *x: None  # noqa: E731

    if not callable(on_exception):
        on_exception = functools.partial(print, on_exception, file=sys.stderr)

    function = getattr(subprocess, name)
    shell = kwargs.get('shell')

    for line in split_commands(commands, echo):
        cmd = shlex.split(line, comments=True)
        if shell:
            cmd = ' '.join(shlex.quote(c) for c in cmd)

        try:
            result = function(cmd, *args, **kwargs)

        except Exception:
            if not on_exception:
                raise
            on_exception(line)

        else:
            yield result


def split_commands(lines, echo=None):
    waiting = []

    def emit():
        parts = ''.join(waiting).strip()
        waiting.clear()
        if parts:
            yield parts

    if isinstance(lines, str):
        lines = lines.splitlines()

    for line in lines:
        echo and echo(line)

        if line.endswith('\\'):
            no_comments = ' '.join(shlex.split(line[:-1], comments=True))
            if line.count('#') > no_comments.count('#'):
                raise ValueError('Comments cannot contain a line continuation')

            waiting.append(line[:-1])

        else:
            waiting.append(line)
            yield from emit()

    yield from emit()


def _wrap(name, summary):
    def wrapped(
        commands,
        *args,
        iterate=False,
        encoding='utf8',
        on_exception=None,
        echo=False,
        merge=False,
        always_list=False,
        **kwargs,
    ):
        kwargs.update(echo=echo, encoding=encoding, on_exception=on_exception)
        if merge:
            kwargs.update(stderr=subprocess.STDOUT)
        it = _run(name, commands, *args, **kwargs)
        if iterate:
            return it
        result = list(it)
        return result if always_list or len(result) != 1 else result[0]

    wrapped.__name__ = name
    wrapped.__doc__ = _ARGS.format(function=name, summary=summary)

    return wrapped


_ARGS = """
{summary}
See the help for `subprocess.{function}()` for more information.

Arguments:
  commands:
    A string, which gets split into lines on line endings, or a list of
    strings.

  args:
    Positional arguments to `subprocess.{function}()` (but prefer keyword
    arguments!)

  on_exception:
    If `on_exception` is `False`, the default, exceptions from
    `subprocess.{function}()` are raised as usual.

    If `on_exception` is True, they are ignored.

    If `on_exception` is a callable, the line that caused the exception is
    passed to it.

    If `on_exception` is a string, the line causing the exception
    is printed, prefixed with that string.

  echo:
    If `echo` is `False`, the default, then commands are silently executed.
    If `echo` is `True`, commands are printed prefixed with `$`
    If `echo` is a string, commands are printed prefixed with that string
    If `echo` is callable, then each command is passed to it.

  merge:
    If True, stderr is set to be subprocess.STDOUT

  always_list:
    If True, the result is always a list.
    If False, the result is a list, unless the input is of length 1, when
    the first element is returned.

  iterate:
    If `iterate` is `False`, the default, then a list of results is
    returned.

    Otherwise an iterator of results which is returned, allowing for lazy
    evaluation.

  encoding:
    Like the argument to `subprocess.{function}()`, except the default  is
    `'utf8'`

  kwargs:
    Named arguments passed on to `subprocess.{function}()`
"""

call = _wrap(
    'call',
    """Call `subprocess.call()` on each command.
Return a list of integer returncodes, one for each command executed.""",
)

check_call = _wrap(
    'check_call',
    """Call `subprocess.check_call()` on each command.
If any command has a non-zero returncode, raise `subprocess.CallProcessError`.
""",
)

check_output = _wrap(
    'check_output',
    """Call `subprocess.check_output()` on each command.
If a command has a non-zero exit code, raise a `subprocess.CallProcessError`.
Otherwise, return the results as a list of strings, one for each command.""",
)

run = _wrap(
    'run',
    """Call `subprocess.run()` on each command.
Return a list of `subprocess.CompletedProcess` instances.""",
)

xmod.xmod(run, __name__, mutable=True)
