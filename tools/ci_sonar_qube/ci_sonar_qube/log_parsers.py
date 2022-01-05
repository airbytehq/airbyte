import json
import os
import re
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Callable, TextIO, List, Optional, Mapping, Any

from mypy.errorcodes import error_codes as mypy_error_codes

from .sonar_qube_api import SonarQubeApi

RE_MYPY_LINE = re.compile(r"^(.+):(\d+):(\d+):")


# RE_MYPY_OTHER_LINES = re.compile("")

class IssueSeverity(Enum):
    blocker = "BLOCKER"
    critical = "CRITICAL"
    major = "MAJOR"
    minor = "MINOR"
    info = "info"


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
    return {f"[{err.code}]": Rule(
        rule_type=Rule.Type.code_smell,
        key=err.code,
        name=err.code.replace("-", " ").capitalize() + " (mypy)",
        description=err.description,
        tool_name="mypy",
        severity=IssueSeverity.minor,
        template="python:CommentRegularExpression"
    ) for err in mypy_error_codes.values()}


class LogParser(SonarQubeApi):
    _mypy_rules: Mapping[str, Rule] = generate_mypy_rules()

    @dataclass
    class Issue:
        path: str
        line_number: int
        column_number: int
        rule: Rule
        description: str

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
                self.logger.info(f"the file {self.output_file} was updated")
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
            "issues": [
                {
                    "engineId": issue.rule.tool_name,
                    "ruleId": issue.rule.sq_key,
                    "severity": issue.rule.severity.value,
                    "type": issue.rule.rule_type.value,
                    "primaryLocation": {
                        "message": issue.description,
                        "filePath": issue.path,
                        "textRange": {
                            "startLine": issue.line_number,
                            "endLine": issue.line_number,
                            "startColumn": issue.column_number,
                            "endColumn": issue.column_number
                        }
                    }

                } for issue in issues]
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
        if len(lines) < 1:
            return None
        path, line_number, column_number, error_or_note, *others = " ".join(lines).split(":")
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
            cls.logger.warning(f"couldn't parse the lines: {lines}")
            return None

        description = others.split("^")[0]

        return cls.Issue(
            path=path.strip(),
            line_number=int(line_number.strip()),
            column_number=int(column_number.strip()),
            description=description.strip(),
            rule=rule,
        )
