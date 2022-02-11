import argparse
import sys

from .log_parsers import LogParser
from .sonar_qube_api import SonarQubeApi


def main() -> int:
    convert_key = len(set(["--mypy_log", "--black_diff", "--isort_diff"]) & set(sys.argv)) > 0
    need_print_key = "--print_key" in sys.argv

    parser = argparse.ArgumentParser(description='Working with SonarQube instance.')
    parser.add_argument('--host', help='SonarQube host', required=not need_print_key, type=str)
    parser.add_argument('--token', help='SonarQube token', required=not need_print_key, type=str)
    parser.add_argument('--pr', help='PR unique name. Example: airbyte/1231', type=str, default=None)

    name_value = parser.add_mutually_exclusive_group(required=not convert_key)
    name_value.add_argument('--project', help='Name of future project', type=str)
    name_value.add_argument('--module', help='Name of future module project', type=str)

    command = parser.add_mutually_exclusive_group(required=not convert_key)
    command.add_argument('--print_key', help='Return a generate SonarQube key', action="store_true")
    command.add_argument('--report', help='generate .md file with current issues of a project')
    command.add_argument('--create', help='create a project', action="store_true")
    command.add_argument('--remove', help='remove project', action="store_true")

    parser.add_argument('--mypy_log', help='Path to MyPy Logs', required=False, type=str)
    parser.add_argument('--black_diff', help='Path to Black Diff', required=False, type=str)
    parser.add_argument('--isort_diff', help='Path to iSort Diff', required=False, type=str)
    parser.add_argument('--output_file', help='Path of output file', required=convert_key, type=str)

    args = parser.parse_args()
    if convert_key:
        parser = LogParser(output_file=args.output_file, host=args.host, token=args.token)
        if args.mypy_log:
            return parser.from_mypy(args.mypy_log)
        if args.black_diff:
            return parser.from_black(args.black_diff)
        if args.isort_diff:
            return parser.from_isort(args.isort_diff)
    api = SonarQubeApi(host=args.host, token=args.token, pr_name=args.pr)

    project_name = api.module2project(args.module) if args.module else args.project

    if args.create:
        return 0 if api.create_project(project_name=project_name) else 1
    elif args.remove:
        return 0 if api.remove_project(project_name=project_name) else 1
    elif args.print_key:
        data = api.prepare_project_settings(project_name)
        print(data["project"], file=sys.stdout)
        return 0
    elif args.report:
        return 0 if api.generate_report(project_name=project_name, report_file=args.report) else 1
    api.logger.critical("not set any action...")
    return 1


if __name__ == '__main__':
    sys.exit(main())
