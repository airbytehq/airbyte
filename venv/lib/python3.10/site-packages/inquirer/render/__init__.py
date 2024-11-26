from inquirer.render.console import ConsoleRender


try:
    from .ncourses import CoursesRender  # noqa
except ImportError:
    pass


class Render:
    def __init__(self, impl=ConsoleRender):
        self._impl = impl

    def render(self, question, answers):
        return self._impl.render(question, answers)
