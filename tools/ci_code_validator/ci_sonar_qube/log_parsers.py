import json
import os
import re
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable, TextIO, List, Optional, Mapping, Any

from mypy.errorcodes import error_codes as mypy_error_codes, ErrorCode
from unidiff import PatchSet

from .sonar_qube_api import SonarQubeApi

HERE = Path(os.getcwd())
RE_MYPY_LINE = re.compile(r"^(.+):(\d+):(\d+):")
RE_MYPY_LINE_WO_COORDINATES = re.compile(r"^(.+): error: (.+)")

FORMAT_TIP = "Please go to the repo root and run the command: './gradlew --no-daemon " \
             ":airbyte-integrations:connectors:<connector_name>:airbytePythonFormat'"


class IssueSeverity(Enum):
    blocker = "BLOCKER"
    critical = "CRITICAL"
    major = "MAJOR"
    minor = "MINOR"
    info = "INFO"


@dataclass
class Rule:
    class Type(Enum):
        code_smell = "CODE_SMELL"
        bug = "BUG"
        vulnerability = "VULNERABILITY"
        security_hotspot = "SECURITY_HOTSPOT"

    rule_type: Type
    key: str
    name: str
    description: str
    tool_name: str
    template: str
    severity: IssueSeverity

    @property
    def unique_key(self):
        return f"{self.tool_name}_{self.key}".replace("-", "_")

    @property
    def sq_key(self):
        lang_part = self.template.split(":")[0]
        return f"{lang_part}:{self.tool_name}_{self.key}".replace("-", "_")


def generate_mypy_rules() -> Mapping[str, Rule]:
    try:
        addl_code = ErrorCode(
            code="unknown",
            description="Unknown error",
            category="General",
        )
    except NameError:
        return []
    return {f"[{err.code}]": Rule(
        rule_type=Rule.Type.code_smell,
        key=err.code,
        name=err.code.replace("-", " ").capitalize() + " (mypy)",
        description=err.description,
        tool_name="mypy",
        severity=IssueSeverity.minor,
        template="python:CommentRegularExpression"
    ) for err in list(mypy_error_codes.values()) + [addl_code]}


class LogParser(SonarQubeApi):
    _mypy_rules: Mapping[str, Rule] = generate_mypy_rules()
    _black_rule = Rule(
        rule_type=Rule.Type.code_smell,
        key="need_format",
        name="Should be formatted (black)",
        description=FORMAT_TIP,
        tool_name="black",
        severity=IssueSeverity.minor,
        template="python:CommentRegularExpression"
    )

    _isort_rule = Rule(
        rule_type=Rule.Type.code_smell,
        key="need_format",
        name="Should be formatted (isort)",
        description=FORMAT_TIP,
        tool_name="isort",
        severity=IssueSeverity.minor,
        template="python:CommentRegularExpression"
    )

    @dataclass
    class Issue:
        path: str

        rule: Rule
        description: str

        line_number: int = None  # 1-indexed
        column_number: int = None  # 1-indexed

        def to_json(self):
            data = {
                "engineId": self.rule.tool_name,
                "ruleId": self.rule.sq_key,
                "severity": self.rule.severity.value,
                "type": self.rule.rule_type.value,
                "primaryLocation": {
                    "message": self.description,
                    "filePath": self.checked_path,
                }
            }
            if self.line_number is not None:
                data["primaryLocation"]["textRange"] = {
                    "startLine": self.line_number,
                    "endLine": self.line_number,
                    "startColumn": self.column_number - 1,  # 0-indexed
                    "endColumn": self.column_number,  # 0-indexed
                }
            return data

        @property
        def checked_path(self):
            if self.path.startswith(str(HERE) + "/"):
                # remove a parent part of path
                return self.path[len(str(HERE) + "/"):].strip()
            return self.path.strip()

    def __init__(self, output_file: str, host: str, token: str):
        super().__init__(host=host, token=token, pr_name="0")
        self.output_file = output_file

    def prepare_file(func: Callable) -> Callable:
        def intra(self, input_file: str) -> int:
            if not os.path.exists(input_file):
                self.logger.critical(f"not found input file: {input_file}")
            with open(input_file, "r") as file:
                issues = func(self, file)
                self._save_all_rules(issues)
                data = self._issues2dict(issues)
                with open(self.output_file, "w") as output_file:
                    output_file.write(json.dumps(data))
                self.logger.info(f"the file {self.output_file} was updated with {len(issues)} issues")
                return 0
            return 1

        return intra

    def _save_all_rules(self, issues: List[Issue]) -> bool:
        """Checks and create SQ rules if needed"""
        if not issues:
            return False
        rules = defaultdict(list)
        for issue in issues:
            rules[issue.rule.tool_name].append(issue.rule)
        for tool_name, tool_rules in rules.items():
            exist_rules = [rule["key"] for rule in self._get_list(f"rules/search?include_external=true&q={tool_name}", "rules")]
            grouped_rules = {rule.sq_key: rule for rule in tool_rules}
            for sq_key, rule in grouped_rules.items():
                if sq_key in exist_rules:
                    # was created before
                    continue
                self.logger.info(f"try to create the rule: {sq_key}")
                body = {
                    "custom_key": rule.unique_key,
                    "markdown_description": rule.description,
                    "name": rule.name,
                    "severity": rule.severity.value,
                    "type": rule.rule_type.value,
                    "template_key": rule.template
                }
                self._post("rules/create", body)
                self.logger.info(f"the rule {sq_key} was created")
        return True

    def _issues2dict(self, issues: List[Issue]) -> Mapping[str, Any]:
        """
         {
            "issues": [
                {
                    "engineId": "test",
                    "ruleId": "rule1",
                    "severity":"BLOCKER",
                    "type":"CODE_SMELL",
                    "primaryLocation": {
                        "message": "fully-fleshed issue",
                        "filePath": "sources/A.java",
                        "textRange": {
                            "startLine": 30,
                            "endLine": 30,
                            "startColumn": 9,
                            "endColumn": 14
                        }
                    }
                },
                ...
        ]}"""
        return {
            "issues": [issue.to_json() for issue in issues]
        }

    @prepare_file
    def from_mypy(self, file: TextIO) -> List[Issue]:
        buff = None
        items = []

        for line in file:
            line = line.strip()
            if RE_MYPY_LINE.match(line):
                if buff:
                    items.append(self.__parse_mypy_issue(buff))
                buff = []
            if buff is not None:
                buff.append(line)
        if buff is None:
            # mypy can return an error without line/column values
            file.seek(0)
            for line in file:
                m = RE_MYPY_LINE_WO_COORDINATES.match(line.strip())
                if not m:
                    continue
                items.append(self.Issue(
                    path=m.group(1).strip(),
                    description=m.group(2).strip(),
                    rule=self._mypy_rules["[unknown]"],
                ))
                self.logger.info(f"detected an error without coordinates: {line}")

        items.append(self.__parse_mypy_issue(buff))
        return [i for i in items if i]

    @classmethod
    def __parse_mypy_issue(cls, lines: List[str]) -> Optional[Issue]:
        """"
        An example of log response:
            source_airtable/helpers.py:8:1: error: Library stubs not installed for
            "requests" (or incompatible with Python 3.7)  [import]
            import requests
            ^
            source_airtable/helpers.py:8:1: note: Hint: "python3 -m pip install types-requests"
        """
        if not lines:
            return None
        path, line_number, column_number, error_or_note, *others = " ".join(lines).split(":")
        if "test" in Path(path).name:
            cls.logger.info(f"skip the test file: {path}")
            return None
        if error_or_note.strip() == "note":
            return None
        others = ":".join(others)
        rule = None
        for code in cls._mypy_rules:
            if code in others:
                rule = cls._mypy_rules[code]
                others = re.sub(r"\s+", " ", others.replace(code, ". Code line: "))
                break
        if not rule:
            cls.logger.warning(f"couldn't find the  rule with '{others}' and lines: {lines}, available rules: {cls._mypy_rules}")
            return None

        description = others.split("^")[0]

        return cls.Issue(
            path=path.strip(),
            line_number=int(line_number.strip()),
            column_number=int(column_number.strip()),
            description=description.strip(),
            rule=rule,
        )

    @staticmethod
    def __parse_diff(lines: List[str]) -> Mapping[str, int]:
        """Converts diff lines to mapping:
           {file1: <updated_code_part1>, file2: <updated_code_part2>}
        """
        patch = PatchSet(lines, metadata_only=True)
        return {updated_file.path: len(updated_file) for updated_file in patch}

    @prepare_file
    def from_black(self, file: TextIO) -> List[Issue]:
        return [self.Issue(
            path=path,
            description=f"{count} code part(s) should be updated.",
            rule=self._black_rule,
        ) for path, count in self.__parse_diff(file.readlines()).items()]

    @prepare_file
    def from_isort(self, file: TextIO) -> List[Issue]:
        changes = defaultdict(lambda: 0)
        for path, count in self.__parse_diff(file.readlines()).items():
            # check path value
            # path in isort diff file has the following format
            # <absolute path>:before|after
            if path.endswith(":before"):
                path = path[:-len(":before")]
            elif path.endswith(":after"):
                path = path[:-len(":after")]
            changes[path] += count

        return [self.Issue(
            path=path,
            description=f"{count} code part(s) should be updated.",
            rule=self._isort_rule,
        ) for path, count in changes.items()]
