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


# Templates


def render_connector_registry_locations_html(destinations_table_html: str, sources_table_html: str) -> str:
    env = Environment(loader=PackageLoader("orchestrator", "templates"))
    template = env.get_template("connector_registry_locations.html")
    return template.render(destinations_table_html=destinations_table_html, sources_table_html=sources_table_html)
