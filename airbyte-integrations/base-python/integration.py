import logging

class AirbyteSpec(object):
    def __init__(self, spec_string):
        self.spec_string = spec_string


class AirbyteCheckResponse(object):
    def __init__(self, successful, field_to_error):
        self.successful = successful
        self.field_to_error = field_to_error


class AirbyteSchema(object):
    def __init__(self, schema):
        self.schema = schema


class AirbyteConfig(object):
    def __init__(self, config_string):
        self.config_string = config_string

class AirbyteMessage(object):
    def __init__(self, message_string):
        self.message_string = message_string


class Integration(object):
    def __init__(self):
        pass

    def spec(self) -> AirbyteSpec:
        raise Exception("Not Implemented")

    # default version reads the config_path to a string
    # this will often be overwritten to add fields for easy consumption or to modify the string for delegating to singer
    def read_config(self, config_path) -> AirbyteConfig:
        with open(config_path, 'r') as file:
            contents = file.read()
        return AirbyteConfig(contents)

    def render_config(self, config_object, rendered_config_path):
        with open(rendered_config_path, 'w') as fh:
            fh.write(config_object.config_string)

    def check(self, config_object, rendered_config_path) -> AirbyteCheckResponse:
        raise Exception("Not Implemented")

    def discover(self, config_object, rendered_config_path) -> AirbyteSchema:
        raise Exception("Not Implemented")
