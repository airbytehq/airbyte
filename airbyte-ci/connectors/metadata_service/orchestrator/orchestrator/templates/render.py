import pandas as pd
import urllib.parse
import json

from jinja2 import Environment, PackageLoader
from typing import List, Optional, Callable, Any
from dataclasses import dataclass
from datetime import timedelta
from orchestrator.utils.object_helpers import deep_copy_params


# 🔗 HTML Renderers


def simple_link_html(url: str) -> str:
    if not url:
        return None

    return f'<a href="{url}" target="_blank">🔗 Link</a>'


def icon_image_html(icon_url: str) -> str:
    if not icon_url:
        return None

    icon_size = "30"
    return f'<img src="{icon_url}" height="{icon_size}" height="{icon_size}"/>'


def test_badge_html(test_summary_url: str) -> str:
    if not test_summary_url:
        return None

    report_url = f"{test_summary_url}/index.html"
    image_shield_base = "https://img.shields.io/endpoint"
    icon_url = f"{test_summary_url}/badge.json"
    icon_url_encoded = urllib.parse.quote(icon_url)
    icon_image = f'<img src="{image_shield_base}?url={icon_url_encoded}">'
    return f'<a href="{report_url}" target="_blank">{icon_image}</a>'


# Dataframe to HTML


@dataclass
class ColumnInfo:
    column: str
    title: str
    formatter: Optional[Callable[[Any], str]] = None


def dataframe_to_table_html(df: pd.DataFrame, column_mapping: List[ColumnInfo]) -> str:
    """
    Convert a dataframe to an HTML table.
    """

    # convert true and false to checkmarks and x's
    df.replace({True: "✅", False: "❌"}, inplace=True)

    title_mapping = {column_info["column"]: column_info["title"] for column_info in column_mapping}

    df.rename(columns=title_mapping, inplace=True)

    html_formatters = {column_info["title"]: column_info["formatter"] for column_info in column_mapping if "formatter" in column_info}

    columns = [column_info["title"] for column_info in column_mapping]

    return df.to_html(
        columns=columns,
        justify="left",
        index=False,
        formatters=html_formatters,
        escape=False,
        classes="styled-table",
        na_rep="❌",
        render_links=True,
    )


def value_to_emoji(value: Any) -> str:
    if value is True:
        return "✅"
    elif value is False:
        return "❌"
    elif value is None or pd.isna(value):
        return "❓"
    else:
        return str(value)


def calculated_report_columns(row: pd.Series) -> dict:
    # Add a new column called past_runs
    # This column will be a string of checkmarks and x's from oldest to newest "❌❌✅❓✅✅✅✅✅❌"
    past_runs = "".join([value_to_emoji(value) for value in row])

    # if there is only one build, then the second to last build status cannot be determined, and we will default to true
    last_build_status = row.iloc[-1]
    second_to_last_build_status = True if len(row) == 1 else row.iloc[-2]

    only_failed_last_build = last_build_status == False and second_to_last_build_status == True
    failed_last_build_two_builds = last_build_status == False and second_to_last_build_status == False

    test_report_url = f"https://connectors.airbyte.com/files/generated_reports/test_summary/{row.name}/index.html"

    return {
        "past_runs": past_runs,
        "last_build_status": last_build_status,
        "only_failed_last_build": only_failed_last_build,
        "failed_last_build_two_builds": failed_last_build_two_builds,
        "test_report_url": test_report_url,
    }


def enhance_nightly_report(nightly_report_df: pd.DataFrame) -> str:
    nightly_report_df = nightly_report_df.reindex(sorted(nightly_report_df.columns), axis=1)

    calculated_report_columns_df = nightly_report_df.apply(lambda row: calculated_report_columns(row), axis="columns", result_type="expand")
    enhance_nightly_report_df = pd.concat([nightly_report_df, calculated_report_columns_df], axis="columns")

    return enhance_nightly_report_df


def nightly_report_df_to_md(nightly_report_df: pd.DataFrame) -> str:
    return nightly_report_df[["past_runs", "test_report_url"]].to_markdown(index=True)


def get_stats_for_connector_type(enhanced_nightly_report_df: pd.DataFrame, connector_type: str) -> str:
    specific_connector_type_df = enhanced_nightly_report_df[enhanced_nightly_report_df.index.str.contains(connector_type)]

    total = len(specific_connector_type_df)
    tested = len(specific_connector_type_df[specific_connector_type_df["last_build_status"].notna()])
    success = len(specific_connector_type_df[specific_connector_type_df["last_build_status"] == True])
    failure = len(specific_connector_type_df[specific_connector_type_df["last_build_status"] == False])

    # Safely calculate percentage and Handle the case where there are no tests, or divide by zero
    success_percent = 0
    if tested > 0:
        success_percent = round(success / tested * 100, 2)

    return {
        "total": total,
        "tested": tested,
        "success": success,
        "failure": failure,
        "success_percent": success_percent,
    }


def get_latest_nightly_report_df(nightly_report_complete_df: pd.DataFrame) -> pd.DataFrame:
    nightly_report_complete_df = nightly_report_complete_df.sort_values(by=["parent_prefix"])
    latest_run = nightly_report_complete_df.iloc[-1]

    return latest_run


# Templates


def render_connector_registry_locations_html(destinations_table_html: str, sources_table_html: str) -> str:
    env = Environment(loader=PackageLoader("orchestrator", "templates"))
    template = env.get_template("connector_registry_locations.html")
    return template.render(destinations_table_html=destinations_table_html, sources_table_html=sources_table_html)


def render_connector_nightly_report_md(nightly_report_connector_matrix_df: pd.DataFrame, nightly_report_complete_df: pd.DataFrame) -> str:
    env = Environment(loader=PackageLoader("orchestrator", "templates"))
    template = env.get_template("connector_nightly_report.md")

    enhanced_nightly_report_df = enhance_nightly_report(nightly_report_connector_matrix_df)
    failed_last_build_only_df = enhanced_nightly_report_df[enhanced_nightly_report_df["only_failed_last_build"] == True]
    failed_last_build_two_builds_df = enhanced_nightly_report_df[enhanced_nightly_report_df["failed_last_build_two_builds"] == True]

    total_connectors = len(nightly_report_connector_matrix_df)

    source_stats = get_stats_for_connector_type(enhanced_nightly_report_df, "source")
    destination_stats = get_stats_for_connector_type(enhanced_nightly_report_df, "destination")

    latest_run = get_latest_nightly_report_df(nightly_report_complete_df)
    last_action_url = latest_run["gha_workflow_run_url"]
    last_action_date = latest_run["run_timestamp"]
    last_action_run_duration_seconds = latest_run["run_duration"]
    last_action_run_duration_human_readable = str(timedelta(seconds=last_action_run_duration_seconds))

    return template.render(
        total_connectors=total_connectors,
        last_action_url=last_action_url,
        last_action_date=last_action_date,
        last_action_run_time=last_action_run_duration_human_readable,
        source_stats=source_stats,
        destination_stats=destination_stats,
        failed_last_build_only=nightly_report_df_to_md(failed_last_build_only_df),
        failed_last_build_only_count=len(failed_last_build_only_df),
        failed_last_build_two_builds=nightly_report_df_to_md(failed_last_build_two_builds_df),
        failed_last_build_two_builds_count=len(failed_last_build_two_builds_df),
    )


@deep_copy_params
def render_connector_test_summary_html(connector_name: str, connector_test_summary_df: pd.DataFrame) -> str:
    env = Environment(loader=PackageLoader("orchestrator", "templates"))
    template = env.get_template("connector_test_summary.html")
    columns_to_show: List[ColumnInfo] = [
        {
            "column": "date",
            "title": "Date",
        },
        {
            "column": "connector_version",
            "title": "Version",
        },
        {
            "column": "success",
            "title": "Success",
        },
        {
            "column": "html_report_url",
            "title": "Test report",
            "formatter": simple_link_html,
        },
        {
            "column": "gha_workflow_run_url",
            "title": "Github Action",
            "formatter": simple_link_html,
        },
    ]

    connector_test_summary_html = dataframe_to_table_html(connector_test_summary_df, columns_to_show)

    return template.render(connector_name=connector_name, connector_test_summary_html=connector_test_summary_html)


@deep_copy_params
def render_connector_test_badge(test_summary: pd.DataFrame) -> str:
    number_of_passes = len(test_summary[test_summary["success"] == True])
    number_of_fails = len(test_summary[test_summary["success"] == False])
    latest_test = test_summary.iloc[0]

    logo_svg_string = '<svg version="1.0" xmlns="http://www.w3.org/2000/svg"\n width="32.000000pt" height="32.000000pt" viewBox="0 0 32.000000 32.000000"\n preserveAspectRatio="xMidYMid meet">\n\n<g transform="translate(0.000000,32.000000) scale(0.100000,-0.100000)"\nfill="#000000" stroke="none">\n<path d="M136 279 c-28 -22 -111 -157 -102 -166 8 -8 34 16 41 38 8 23 21 25\n29 3 3 -8 -6 -35 -20 -60 -18 -31 -22 -44 -12 -44 20 0 72 90 59 103 -6 6 -11\n27 -11 47 0 77 89 103 137 41 18 -23 16 -62 -5 -96 -66 -109 -74 -125 -59\n-125 24 0 97 140 97 185 0 78 -92 123 -154 74z"/>\n<path d="M168 219 c-22 -13 -23 -37 -2 -61 12 -12 14 -22 7 -30 -5 -7 -22 -34\n-37 -60 -20 -36 -23 -48 -12 -48 13 0 106 147 106 169 0 11 -28 41 -38 41 -4\n0 -15 -5 -24 -11z m32 -34 c0 -8 -4 -15 -10 -15 -5 0 -10 7 -10 15 0 8 5 15\n10 15 6 0 10 -7 10 -15z"/>\n</g>\n</svg>\n'

    message = ""
    color = "red"
    if number_of_passes > 0:
        message += f"✔ {number_of_passes}"

    if number_of_passes > 0 and number_of_fails > 0:
        color = "yellow"
        message += " | "

    if number_of_fails > 0:
        message += f"✘ {number_of_fails}"

    if latest_test["success"] == True:
        color = "green"

    badge_dict = {
        "schemaVersion": 1,
        "label": "",
        "labelColor": "#c5c4ff",
        "message": message,
        "color": color,
        "cacheSeconds": 300,
        "logoSvg": logo_svg_string,
    }

    json_string = json.dumps(badge_dict)

    return json_string
