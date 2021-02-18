from .base_schema import BaseSchema


class BlobSchema(BaseSchema):

    def get(self):
        return {'type': 'object'}
