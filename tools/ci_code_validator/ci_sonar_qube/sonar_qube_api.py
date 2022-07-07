import itertools
import re
from functools import reduce
from typing import Mapping, Any, Optional, List
from urllib.parse import urljoin

import requests
from mdutils.mdutils import MdUtils
from requests.auth import HTTPBasicAuth

from ci_common_utils import Logger

AIRBYTE_PROJECT_PREFIX = "airbyte"
RE_RULE_NAME = re.compile(r"(.+):[A-Za-z]+(\d+)")

REPORT_METRICS = (
    "alert_status",
    # "quality_gate_details",
    "bugs", "new_bugs",
    "reliability_rating", "new_reliability_rating",
    "vulnerabilities", "new_vulnerabilities",
    "security_rating", "new_security_rating",
    # "security_hotspots", "new_security_hotspots",
    # "security_hotspots_reviewed", "new_security_hotspots_reviewed",
    # "security_review_rating", "new_security_review_rating",
    "code_smells", "new_code_smells",
    # "sqale_rating", "new_maintainability_rating",
    # "sqale_index", "new_technical_debt",
    "coverage", "new_coverage",
    "lines_to_cover", "new_lines_to_cover",
    "tests",
    "duplicated_lines_density", "new_duplicated_lines_density",
    "duplicated_blocks",
    "ncloc",
    # "ncloc_language_distribution",
    # "projects",
    # "lines", "new_lines"
)

RATINGS = {
    1.0: "A",
    2.0: "B",
    3.0: "C",
    4.0: "D",
    5.0: "F",
}


class SonarQubeApi:
    """https://sonarcloud.io/web_api"""
    logger = Logger()

    def __init__(self, host: str, token: str, pr_name: str):

        self._host = host
        self._token = token

        # split the latest name part
        self._pr_id = (pr_name or '').split("/")[-1]
        if not self._pr_id.isdigit():
            self.logger.critical(f"PR id should be integer. Current value: {pr_name}")

        self._pr_id = int(self._pr_id)
        # check token
        # https://sonarcloud.io/web_api/api/authentication/validate
        if not self._host:
            return
        resp = self._get("authentication/validate")
        if not resp["valid"]:
            self.logger.critical("provided token is not valid")

    @property
    def __auth(self):
        return HTTPBasicAuth(self._token, '')

    def __parse_response(self, url: str, response: requests.Response) -> Mapping[str, Any]:
        if response.status_code == 204:
            # empty response
            return {}
        elif response.status_code != 200:
            self.logger.critical(f"API error for {url}: [{response.status_code}] {response.json()['errors']}")
        return response.json()

    def generate_url(self, endpoint: str) -> str:
        return reduce(urljoin, [self._host, "/api/", endpoint])

    def _post(self, endpoint: str, json: Mapping[str, Any]) -> Mapping[str, Any]:
        url = self.generate_url(endpoint)
        return self.__parse_response(url, requests.post(url, auth=self.__auth, params=json, json=json))

    def _get(self, endpoint: str) -> Mapping[str, Any]:
        url = self.generate_url(endpoint)
        return self.__parse_response(url, requests.get(url, auth=self.__auth))

    def _get_list(self, endpoint: str, list_name: str) -> List[Mapping[str, Any]]:

        page = 0
        items = []
        while True:
            page += 1
            url = endpoint + "&" if "?" in endpoint else "?" + f"p={page}"
            data = self._get(url)
            items += data[list_name]
            total = data.get("total") or data.get("paging", {}).get("total", 0)
            if len(items) >= total:
                break
        return items

    @classmethod
    def module2project(cls, module_name: str) -> str:
        """"""
        parts = module_name.split("/")
        if len(parts) != 2:
            cls.logger.critical("module name must have the format: component/module")
        return f"{AIRBYTE_PROJECT_PREFIX}:{parts[0].lower()}:{parts[1].lower().replace('_', '-')}"

    def __correct_project_name(self, project_name: str) -> str:
        return f"pr:{self._pr_id}:{project_name}" if self._pr_id else f"master:{project_name}"

    def __search_project(self, project_name: str) -> Optional[Mapping[str, Any]]:
        """https://sonarcloud.io/web_api/api/projects/search"""
        data = self._get(f"projects/search?q={project_name}")
        exists_projects = data["components"]
        if len(exists_projects) > 1:
            self.logger.critical(f"there are several projects with the name '{project_name}'")
        elif len(exists_projects) == 0:
            return None
        return exists_projects[0]

    def prepare_project_settings(self, project_name: str) -> Mapping[str, str]:
        title = re.sub('[:_-]', ' ', project_name).replace("connectors_", "").title()
        if self._pr_id:
            title += f"(#{self._pr_id})"

        project_name = self.__correct_project_name(project_name)
        return {
            "name": title,
            "project": project_name,
            "visibility": "private",
        }

    def create_project(self, project_name: str) -> bool:
        """https://sonarcloud.io/web_api/api/projects/create"""
        data = self.prepare_project_settings(project_name)
        project_name = data["project"]
        exists_project = self.__search_project(project_name)
        if exists_project:
            self.logger.info(f"The project '{project_name}' was created before")
            return True

        self._post("projects/create", data)
        self.logger.info(f"The project '{project_name}' was created")
        return True

    def remove_project(self, project_name: str) -> bool:
        """https://sonarcloud.io/web_api/api/projects/delete"""
        project_name = self.prepare_project_settings(project_name)["project"]

        exists_project = self.__search_project(project_name)
        if exists_project is None:
            self.logger.info(f"not found the project '{project_name}'")
            return True
        body = {
            "project": project_name
        }
        self._post("projects/delete", body)
        self.logger.info(f"The project '{project_name}' was removed")
        return True

    def generate_report(self, project_name: str, report_file: str) -> bool:
        project_data = self.prepare_project_settings(project_name)

        md_file = MdUtils(file_name=report_file)
        md_file.new_line("<details><summary> <strong> SonarQube Report </strong></summary>")
        md_file.new_line("<p>")
        md_file.new_line("")
        md_file.new_line(f'### SonarQube report for {project_data["name"]}')

        project_name = project_data["project"]

        issues = self._get_list(f"issues/search?componentKeys={project_name}&additionalFields=_all", "issues")
        rules = {}
        for rule_key in set(issue["rule"] for issue in issues):
            key_parts = rule_key.split(":")
            while len(key_parts) > 2:
                key_parts.pop(0)
            key = ":".join(key_parts)

            data = self._get(f"rules/search?rule_key={key}")["rules"]
            if not data:
                data = self._get(f"rules/show?key={rule_key}")["rule"]
            else:
                data = data[0]

            description = data["name"]
            public_name = key
            link = None
            if rule_key.startswith("external_"):
                public_name = key.replace("external_", "")
                if not data["isExternal"]:
                    # this is custom rule
                    description = data["htmlDesc"]
                if public_name.startswith("flake"):
                    # single link for all descriptions
                    link = "https://flake8.pycqa.org/en/latest/user/error-codes.html"
                elif "isort_" in public_name:
                    link = "https://pycqa.github.io/isort/index.html"
                elif "black_" in public_name:
                    link = "https://black.readthedocs.io/en/stable/the_black_code_style/index.html"
            else:
                # link's example
                # https://rules.sonarsource.com/python/RSPEC-6287
                m = RE_RULE_NAME.match(public_name)
                if not m:
                    # for local server
                    link = f"{self._host}coding_rules?open={key}&rule_key={key}"
                else:
                    # to public SQ docs
                    link = f"https://rules.sonarsource.com/{m.group(1)}/RSPEC-{m.group(2)}"
            if link:
                public_name = md_file.new_inline_link(
                    link=link,
                    text=public_name
                )

            rules[rule_key] = (public_name, description)

        data = self._get(f"measures/component?component={project_name}&additionalFields=metrics&metricKeys={','.join(REPORT_METRICS)}")
        measures = {}
        total_coverage = None
        for measure in data["component"]["measures"]:
            metric = measure["metric"]
            if measure["metric"].startswith("new_") and measure.get("periods"):
                # we need to show values for last sync period only
                last_period = max(measure["periods"], key=lambda period: period["index"])
                value = last_period["value"]
            else:
                value = measure.get("value")
            measures[metric] = value
        # group overall and latest values
        measures = {metric: (value, measures.get(f"new_{metric}")) for metric, value in measures.items() if
                    not metric.startswith("new_")}
        metrics = {}
        for metric in data["metrics"]:
            # if metric["key"] not in measures:
            #     continue
            metrics[metric["key"]] = (metric["name"], metric["type"])

        md_file.new_line('#### Measures')

        values = []
        for metric, (overall_value, latest_value) in measures.items():
            if metric not in metrics:
                continue
            name, metric_type = metrics[metric]
            value = overall_value if (latest_value is None or latest_value == "0") else latest_value

            if metric_type == "PERCENT":
                value = str(round(float(value), 1))
            elif metric_type == "INT":
                value = int(float(value))
            elif metric_type == "LEVEL":
                pass
            elif metric_type == "RATING":
                value = int(float(value))
                for k, v in RATINGS.items():
                    if value <= k:
                        value = v
                        break
            if metric == "coverage":
                total_coverage = value
            values.append([name, value])

        values += [
            ("Blocker Issues", sum(map(lambda i: i["severity"] == "BLOCKER", issues))),
            ("Critical Issues", sum(map(lambda i: i["severity"] == "CRITICAL", issues))),
            ("Major Issues", sum(map(lambda i: i["severity"] == "MAJOR", issues))),
            ("Minor Issues", sum(map(lambda i: i["severity"] == "MINOR", issues))),
        ]

        while len(values) % 3:
            values.append(("", ""))
        table_items = ["Name", "Value"] * 3 + list(itertools.chain.from_iterable(values))
        md_file.new_table(columns=6, rows=int(len(values) / 3 + 1), text=table_items, text_align='left')
        md_file.new_line()
        if issues:
            md_file.new_line('#### Detected Issues')
            table_items = [
                "Rule", "File", "Description", "Message"
            ]
            for issue in issues:
                rule_name, description = rules[issue["rule"]]
                path = issue["component"].split(":")[-1].split("/")
                # need to show only 2 last path parts
                while len(path) > 2:
                    path.pop(0)
                path = "/".join(path)

                # add line number in the end
                if issue.get("line"):
                    path += f':{issue["line"]}'
                table_items += [
                    f'{rule_name} ({issue["severity"]})',
                    path,
                    description,
                    issue["message"],
                ]

            md_file.new_table(columns=4, rows=len(issues) + 1, text=table_items, text_align='left')
        coverage_files = [(k, v) for k, v in self.load_coverage_component(project_name).items()]
        if total_coverage is not None:
            md_file.new_line(f'#### Coverage ({total_coverage}%)')
            while len(coverage_files) % 2:
                coverage_files.append(("", ""))
            table_items = ["File", "Coverage"] * 2 + list(itertools.chain.from_iterable(coverage_files))
            md_file.new_table(columns=4, rows=int(len(coverage_files) / 2 + 1), text=table_items, text_align='left')
        md_file.new_line("")
        md_file.new_line("</p>")
        md_file.new_line("</details>")
        md_file.create_md_file()
        self.logger.info(f"The {report_file} was generated")
        return True

    def load_coverage_component(self, base_component: str, dir_path: str = None) -> Mapping[str, Any]:

        page = 0
        coverage_files = {}
        read_count = 0
        while True:
            page += 1
            component = base_component
            if dir_path:
                component += f":{dir_path}"
            url = f"measures/component_tree?p={page}&component={component}&additionalFields=metrics&metricKeys=coverage,uncovered_lines,uncovered_conditions&strategy=children"
            data = self._get(url)
            read_count += len(data["components"])
            for component in data["components"]:
                if component["qualifier"] == "DIR":
                    coverage_files.update(self.load_coverage_component(base_component, component["path"]))
                    continue
                elif not component["measures"]:
                    continue
                elif component["qualifier"] == "FIL":
                    coverage_files[component["path"]] = [m["value"] for m in component["measures"] if m["metric"] == "coverage"][0]
            if data["paging"]["total"] <= read_count:
                break

        return coverage_files
