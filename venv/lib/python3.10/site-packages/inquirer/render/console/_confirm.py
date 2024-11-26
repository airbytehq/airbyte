from readchar import key

from inquirer import errors
from inquirer.render.console.base import BaseConsoleRender


class Confirm(BaseConsoleRender):
    title_inline = True

    def get_header(self):
        confirm = "(Y/n)" if self.question.default else "(y/N)"
        return f"{self.question.message} {confirm}"

    def process_input(self, pressed):
        if pressed == key.CTRL_C:
            raise KeyboardInterrupt()

        if pressed.lower() == key.ENTER:
            raise errors.EndOfInput(self.question.default)

        if pressed in "yY":
            print(pressed)
            raise errors.EndOfInput(True)
        if pressed in "nN":
            print(pressed)
            raise errors.EndOfInput(False)
