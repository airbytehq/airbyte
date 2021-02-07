from .base_schema import BaseSchema


class StaticSchema(BaseSchema):

    def get(self):
        return self.options.value
