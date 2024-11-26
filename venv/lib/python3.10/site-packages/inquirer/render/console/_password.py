from inquirer.render.console._text import Text


class Password(Text):
    def get_current_value(self):
        return self.question.echo * len(self.current) + (self.terminal.move_left * self.cursor_offset)

    def handle_validation_error(self, error):
        if error.reason:
            return error.reason

        return f"Entered value is not a valid {self.question.name}."
