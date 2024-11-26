from readchar import key

from inquirer import errors
from inquirer.render.console.base import BaseConsoleRender


class Text(BaseConsoleRender):
    title_inline = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current = self.question.default or ""
        self.cursor_offset = 0
        self._autocomplete_state = None

    def get_current_value(self):
        return self.current + (self.terminal.move_left * self.cursor_offset)

    def process_input(self, pressed):
        if pressed == key.CTRL_C:
            raise KeyboardInterrupt()

        if pressed in (key.CR, key.LF, key.ENTER):
            raise errors.EndOfInput(self.current)

        if pressed == key.TAB and self.question.autocomplete:
            if self._autocomplete_state is None:
                self._autocomplete_state = [self.current, 0]

            [text, state] = self._autocomplete_state
            autocomplete = self.question.autocomplete(text, state)
            if isinstance(autocomplete, str):
                self.current = autocomplete
                self._autocomplete_state[1] += 1
            else:
                self._autocomplete_state = None
            return

        self._autocomplete_state = None

        if pressed == key.BACKSPACE:
            if self.current and self.cursor_offset != len(self.current):
                if self.cursor_offset > 0:
                    n = -self.cursor_offset
                    self.current = self.current[: n - 1] + self.current[n:]
                else:
                    self.current = self.current[:-1]
        elif pressed == key.SUPR:
            if self.current and self.cursor_offset:
                n = -self.cursor_offset
                self.cursor_offset -= 1
                if n < -1:
                    self.current = self.current[:n] + self.current[n + 1 :]  # noqa E203
                else:
                    self.current = self.current[:n]
        elif pressed == key.LEFT:
            if self.cursor_offset < len(self.current):
                self.cursor_offset += 1
        elif pressed == key.RIGHT:
            self.cursor_offset = max(self.cursor_offset - 1, 0)
        elif len(pressed) != 1:
            return
        else:
            if self.cursor_offset == 0:
                self.current += pressed
            else:
                n = -self.cursor_offset
                self.current = "".join((self.current[:n], pressed, self.current[n:]))
