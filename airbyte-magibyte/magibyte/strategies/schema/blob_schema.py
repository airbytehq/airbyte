from .base_schema import BaseSchema


class BlobSchema(BaseSchema):

    def get(self):
        return {
            '$schema': 'http://json-schema.org/draft-07/schema#',
            'type': 'object'
        }
