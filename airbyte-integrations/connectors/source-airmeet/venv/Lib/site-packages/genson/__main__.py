import argparse
import sys
import re
import json
from . import SchemaBuilder, __version__


class CLI:
    def __init__(self, prog=None):
        self._make_parser(prog)
        self._prepare_args()
        self.builder = SchemaBuilder(schema_uri=self.args.schema_uri)

    def run(self):
        if not self.args.schema and not self.args.object:
            self.fail('noting to do - no schemas or objects given')
        self.add_schemas()
        self.add_objects()
        self.print_output()

    def add_schemas(self):
        for fp in self.args.schema:
            self._call_with_json_from_fp(self.builder.add_schema, fp)
            fp.close()

    def add_objects(self):
        for fp in self.args.object:
            self._call_with_json_from_fp(self.builder.add_object, fp)
            fp.close()

    def print_output(self):
        print(self.builder.to_json(indent=self.args.indent))

    def fail(self, message):
        self.parser.error(message)

    def _make_parser(self, prog=None):
        file_type = argparse.FileType('r', encoding=self._get_encoding())

        self.parser = argparse.ArgumentParser(
            add_help=False,
            prog=prog,
            description="""Generate one, unified JSON Schema from one or more
            JSON objects and/or JSON Schemas. Compatible with JSON-Schema Draft
            4 and above.""")

        self.parser.add_argument(
            '-h', '--help', action='help', default=argparse.SUPPRESS,
            help='Show this help message and exit.')
        self.parser.add_argument(
            '--version', action='version', default=argparse.SUPPRESS,
            version='%(prog)s {}'.format(__version__),
            help='Show version number and exit.')
        self.parser.add_argument(
            '-d', '--delimiter', metavar='DELIM',
            help="""Set a delimiter. Use this option if the input files
            contain multiple JSON objects/schemas. You can pass any string. A
            few cases ('newline', 'tab', 'space') will get converted to a
            whitespace character. If this option is omitted, the parser will
            try to auto-detect boundaries.""")
        self.parser.add_argument(
            '-e', '--encoding', type=str, metavar='ENCODING',
            help="""Use ENCODING instead of the default system encoding
            when reading files. ENCODING must be a valid codec name or
            alias.""")
        self.parser.add_argument(
            '-i', '--indent', type=int, metavar='SPACES',
            help="""Pretty-print the output, indenting SPACES spaces.""")
        self.parser.add_argument(
            '-s', '--schema', action='append', default=[], type=file_type,
            help="""File containing a JSON Schema (can be specified multiple
            times to merge schemas).""")
        self.parser.add_argument(
            '-$', '--schema-uri', metavar='SCHEMA_URI', dest='schema_uri',
            default=SchemaBuilder.DEFAULT_URI,
            help="""The value of the '$schema' keyword (defaults to {default!r}
            or can be specified in a schema with the -s option). If {null!r} is
            passed, the "$schema" keyword will not be included in the
            result.""".format(default=SchemaBuilder.DEFAULT_URI,
                              null=SchemaBuilder.NULL_URI))
        self.parser.add_argument(
            'object', nargs=argparse.REMAINDER, type=file_type,
            help="""Files containing JSON objects (defaults to stdin if no
            arguments are passed).""")

    def _get_encoding(self):
        """
        use separate arg parser to grab encoding argument before
        defining FileType args
        """
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument('-e', '--encoding', type=str)
        args, _ = parser.parse_known_args()
        return args.encoding

    def _prepare_args(self):
        self.args = self.parser.parse_args()
        self._prepare_delimiter()

        # default to stdin if no objects or schemas
        if not self.args.object and not sys.stdin.isatty():
            self.args.object.append(sys.stdin)

    def _prepare_delimiter(self):
        """
        manage special conversions for difficult bash characters
        """
        if self.args.delimiter == 'newline':
            self.args.delimiter = '\n'
        elif self.args.delimiter == 'tab':
            self.args.delimiter = '\t'
        elif self.args.delimiter == 'space':
            self.args.delimiter = ' '

    def _call_with_json_from_fp(self, method, fp):
        for json_string in self._get_json_strings(fp.read().strip()):
            try:
                json_obj = json.loads(json_string)
            except json.JSONDecodeError as err:
                self.fail('invalid JSON in {}: {}'.format(fp.name, err))
            method(json_obj)

    def _get_json_strings(self, raw_text):
        if self.args.delimiter is None or self.args.delimiter == '':
            json_strings = self._detect_json_strings(raw_text)
        else:
            json_strings = raw_text.split(self.args.delimiter)

        # sanitize data before returning
        return [string.strip() for string in json_strings if string.strip()]

    @staticmethod
    def _detect_json_strings(raw_text):
        """
        Use regex with lookaround to spot the boundaries between JSON
        objects. Unfortunately, it has to match *something*, so at least
        one character must be removed and replaced.
        """
        strings = re.split(r'}\s*(?={)', raw_text)

        # put back the stripped character
        json_strings = [string + '}' for string in strings[:-1]]

        # the last one doesn't need to be modified
        json_strings.append(strings[-1])

        return json_strings


def main():
    CLI().run()


if __name__ == "__main__":
    CLI('genson').run()
