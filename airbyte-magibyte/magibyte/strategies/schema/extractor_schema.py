import logging

from genson import SchemaBuilder

from .base_schema import BaseSchema


class ExtractorSchema(BaseSchema):

    def __init__(self, options, **kwargs):
        super(ExtractorSchema, self).__init__(options, **kwargs)

        self.extractor = self.build_strategy('extractor', options['extractor'], **kwargs)

    def get(self, context):
        sample_size = self.extrapolate(self.options.get('sample_size', 100), context)

        builder = SchemaBuilder('http://json-schema.org/draft-07/schema#')
        builder.add_schema({"type": "object", "properties": {}})

        for _, record in zip(range(sample_size), self.extractor.extract(context)):
            builder.add_object(record)

        return builder.to_schema()
