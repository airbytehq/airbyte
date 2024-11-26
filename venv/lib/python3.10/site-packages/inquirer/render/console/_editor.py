import editor
from readchar import key

from inquirer import errors
from inquirer.render.console.base import BaseConsoleRender


class Editor(BaseConsoleRender):
    title_inline = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current = ""

    def get_current_value(self):
        return "{}Press <enter> to launch your editor{}".format(
            self.theme.Editor.opening_prompt_color, self.terminal.normal
        )

    def handle_validation_error(self, error):
        if error.reason:
            return error.reason

        return f"Entered value is not a valid {self.question.name}."

    def process_input(self, pressed):
        if pressed == key.CTRL_C:
            raise KeyboardInterrupt()

        if pressed in (key.CR, key.LF, key.ENTER):
            data = editor(text=self.question.default or "")
            raise errors.EndOfInput(data)

        raise errors.ValidationError(
            "You have pressed unknown key! " "Press <enter> to open editor or " "CTRL+C to exit."
        )
