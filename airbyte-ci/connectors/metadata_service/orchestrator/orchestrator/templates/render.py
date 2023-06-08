import pandas as pd
import urllib.parse

from jinja2 import Environment, PackageLoader
from typing import List, Optional, Callable, Any
from dataclasses import dataclass
from datetime import timedelta


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

    image_shield_base = "https://img.shields.io/endpoint"
    icon_url = f"{test_summary_url}/badge.json"
    icon_url_encoded = urllib.parse.quote(icon_url)
    icon_image = f'<img src="{image_shield_base}?url={icon_url_encoded}">'
    return f'<a href="{test_summary_url}" target="_blank">{icon_image}</a>'


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

    return {
        "past_runs": past_runs,
        "last_build_status": last_build_status,
        "only_failed_last_build": only_failed_last_build,
        "failed_last_build_two_builds": failed_last_build_two_builds,
    }


def enhance_nightly_report(nightly_report_df: pd.DataFrame) -> str:
    nightly_report_df = nightly_report_df.reindex(sorted(nightly_report_df.columns), axis=1)

    calculated_report_columns_df = nightly_report_df.apply(lambda row: calculated_report_columns(row), axis="columns", result_type="expand")
    enhance_nightly_report_df = pd.concat([nightly_report_df, calculated_report_columns_df], axis="columns")

    return enhance_nightly_report_df


def nightly_report_df_to_md(nightly_report_df: pd.DataFrame) -> str:
    return nightly_report_df[["past_runs"]].to_markdown(index=True)


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
