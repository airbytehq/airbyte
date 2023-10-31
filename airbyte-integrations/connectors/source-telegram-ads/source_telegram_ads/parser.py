import csv
import re
from datetime import datetime
from io import StringIO
from typing import Any, Generator

import requests
from bs4 import BeautifulSoup, Tag
from source_telegram_ads.utils import DEFAULT_USER_AGENT


def request_tg_ads(
    base_url: str,
    endpoint: str,
    user_agent: str,
    account_token: str,
    organization_token: str,
) -> requests.Response:
    return requests.get(
        url=f"{base_url}{endpoint}",
        headers={
            "user-agent": user_agent,
        },
        cookies={
            "stel_token": account_token,
            "stel_adowner": organization_token,
        },
    )


def test_logged_in(account_page_response: requests.Response) -> bool:
    soup = BeautifulSoup(account_page_response.text, features="html.parser")
    return not bool(soup.select("form.login-form"))


def parse_ad_stats(
    ad_stat_page_response: requests.Response, account_token: str, organization_token: str
) -> Generator[dict[str, Any], None, None]:
    try:
        stat_graph_csv_link, budget_graph_csv_link = re.findall(
            '(\/csv\\?prefix=.*)"',
            ad_stat_page_response.text,
        )[:2]
    except:
        return
    get_csv_kwargs = dict(
        base_url="https://promote.telegram.org/",
        user_agent=DEFAULT_USER_AGENT,
        account_token=account_token,
        organization_token=organization_token,
    )
    stat_graph_csv = request_tg_ads(
        **get_csv_kwargs,
        endpoint=stat_graph_csv_link,
    ).text.strip()
    budget_graph_csv = request_tg_ads(
        **get_csv_kwargs,
        endpoint=budget_graph_csv_link,
    ).text.strip()

    default_stat_values = {
        "date": None,
        "Views": 0,
        "Joined": 0,
        "Started bot": 0,
    }
    keys_transform_mapping = {
        "date": "day",
        "Started bot": "started_bot",
        "Views": "views",
        "Joined": "joined",
    }

    stat_graph_reader = csv.reader(StringIO(stat_graph_csv), delimiter="\t")
    stat_graph_header = list(map(lambda s: s.lower(), next(stat_graph_reader)))

    stat_graph_data = {}
    stat_graph_reader = csv.DictReader(StringIO(stat_graph_csv), delimiter="\t")
    for record in stat_graph_reader:
        record = {**default_stat_values, **record}
        for key, replace_key in keys_transform_mapping.items():
            record[replace_key] = record.pop(key)
        day = record.pop("day")
        stat_graph_data[day] = record

    budget_graph_reader = csv.reader(StringIO(budget_graph_csv), delimiter="\t")
    next(budget_graph_reader)
    budget_graph_data = {dt: spent_budget.replace(",", ".") for dt, spent_budget in budget_graph_reader}

    for dt in stat_graph_data.keys():
        yield {
            "day": datetime.strptime(dt, "%d %b %Y").date().isoformat(),
            "spent_budget": float(budget_graph_data[dt]),
            **stat_graph_data[dt],
        }
    return


def parse_all_ads(ads_page_response: requests.Response) -> Generator[dict[str, Any], None, None]:
    with open("parse_all_ads_out.html", "w") as f:
        f.write(ads_page_response.text)
    soup = BeautifulSoup(ads_page_response.text, features="html.parser")
    table: Tag = soup.select("section.pr-content>.table-responsive>table")[0]
    for row in table.select("tbody>tr"):
        row_data = {}
        for cell_n, cell in enumerate(row.select("td>.pr-cell")):
            if cell_n == 0:
                row_data["id"] = cell.select("a")[0]["href"].split("/")[-1]
                row_data["title"] = cell.select("a")[0].contents[0]
            if cell_n == 1:
                row_data["views"] = cell.select("a")[0].contents[0].replace(",", "")
            if cell_n == 11:
                row_data["status"] = cell.select("a")[0].contents[0].lower()
            if cell_n == 12:
                row_data["date_added"] = datetime.strptime(
                    cell.select("a")[0].contents[0],
                    "%d %b %y %H:%M",
                ).isoformat()
        yield row_data
    return


def parse_ad_details(ad_page_response: requests.Response) -> dict[str, Any]:
    soup = BeautifulSoup(ad_page_response.text, features="html.parser")
    ad_details = {}
    target_inputs_ids = ["ad_title", "ad_promote_url", "ad_cpm", "ad_info", "ad_text"]
    all_inputs = soup.select("input, textarea")
    for input_el in all_inputs:
        try:
            input_el["id"]
        except Exception as e:
            continue
        if input_el["id"] in target_inputs_ids:
            input_content = None
            try:
                input_content = input_el.contents[0]
            except:
                pass
            ad_details[input_el["id"]] = input_el.get("value") or input_content

    for select_el in soup.select(".select"):
        try:
            select_el_name = select_el["data-name"]
        except:
            continue
        ad_details[select_el_name] = []
        for select_el_item in select_el.select(".selected-item"):
            ad_details[select_el_name].append(
                {
                    "id": select_el_item.get("data-val"),
                    "name": select_el_item.select(".label")[0].contents[0],
                }
            )
    for key in list(ad_details.keys()):
        replaced_key = key.removeprefix("ad_")
        ad_details[replaced_key] = ad_details.pop(key)
    if "info" not in ad_details.keys():
        try:
            ad_details["info"] = soup.select('label[for="ad_info"]')[0].parent.select("input")[0]["value"]
        except:
            pass
    try:
        ad_details["budget"] = soup.select('label[for="ad_budget"]')[0].parent.select("a")[0].contents[0]
    except:
        pass
    return ad_details
