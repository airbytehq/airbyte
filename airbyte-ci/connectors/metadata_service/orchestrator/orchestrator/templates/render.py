from jinja2 import Environment, PackageLoader
import pandas as pd
from typing import List, Optional, Callable, Any
from dataclasses import dataclass
import urllib.parse


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

def enhance_nightly_report(nightly_report_df: pd.DataFrame) -> str:
    # Each row is indexed by the connector name
    # Each column is the path to the nightly report file
    # The path is in the format of airbyte-ci/connectors/test/{unixtimestamp}/{gitsha}
    # Each cell is true if successful, false is failed, and nan if not run

    # Add a new column called run_history_emoji
    # This column will be a string of checkmarks and x's from oldest to newest "❌❌✅❓✅✅✅✅✅❌"
    nightly_report_df["past_runs"] = nightly_report_df.apply(lambda row: "".join([value_to_emoji(value) for value in row]), axis=1)

    # Add a new column called last_build_status
    # This column will be true if the last build succeeded and false if it failed
    # We have to ignore the past_runs column

    nightly_report_df["last_build_status"] = nightly_report_df.apply(lambda row: row[-2], axis=1)

    # Add a new column called only_failed_last_build
    # This column will be true if the last build failed and the build before that succeeded
    nightly_report_df["only_failed_last_build"] = nightly_report_df.apply(lambda row: row[-2] is False and row[-3] is True, axis=1)

    # Add a new column called failed_last_build_two_builds
    # This column will be true if the last build failed and the build before that failed
    nightly_report_df["failed_last_build_two_builds"] = nightly_report_df.apply(lambda row: row[-2] is False and row[-3] is False, axis=1)

    return nightly_report_df

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
    last_action_url = "TODO"
    last_action_date = "TODO"

    return template.render(
        total_connectors=total_connectors,
        last_action_url=last_action_url,
        last_action_date=last_action_date,
        source_stats=source_stats,
        destination_stats=destination_stats,
        failed_last_build_only=nightly_report_df_to_md(failed_last_build_only_df),
        failed_last_build_only_count=len(failed_last_build_only_df),
        failed_last_build_two_builds=nightly_report_df_to_md(failed_last_build_two_builds_df),
        failed_last_build_two_builds_count=len(failed_last_build_two_builds_df),
    )
