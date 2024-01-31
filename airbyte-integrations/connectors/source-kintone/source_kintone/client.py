import urllib.request
import urllib.parse
import json
import yaml
import base64

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import (
    AirbyteStream,
)


class Client:
    def __init__(self, config: json, logger: AirbyteLogger):
        self.subdomain = config.get("subdomain")
        with open(f"/airbyte/integration_code/source_kintone/app_name_mapping/app_name.yaml") as f:
              self.app_name_mappings = yaml.full_load(f)
        self.field_code_mappings = {}
        for app_id in config.get("app_ids"):
            with open(f"/airbyte/integration_code/source_kintone/field_code_mapping/field_code_{app_id}.yaml") as f:
                  self.field_code_mappings[app_id] = yaml.full_load(f)
        self.logger = logger
        self.config = config

    def _get_base_url(self):
        return "https://" + self.subdomain + ".cybozu.com"

    def _get_base_header(self):
        text = self.config.get("login_id") + ":" + self.config.get("password")
        param = base64.b64encode(text.encode()).decode()
        return {
           "X-Cybozu-Authorization": param,
        }
    
    def _fetch_data(self, url: str, params: dict, use_json: bool = False):
        headers = self._get_base_header()
        if use_json:
            headers["Content-Type"] = "application/json"
            req = urllib.request.Request(
                url=url,
                headers=headers,
                data=json.dumps(params).encode("utf-8"),
                method="GET",
            )
        else:
            url = update_url(url, params)
            req = urllib.request.Request(
                url=url,
                headers=headers,
                method="GET",
            )
        
        return json.load(urllib.request.urlopen(req))


    def _post_data(self, url: str, params: dict):
        headers = self._get_base_header()
        headers["Content-Type"] = "application/json"
        req = urllib.request.Request(
            url=url,
            headers=headers,
            data=json.dumps(params).encode("utf-8"),
            method="POST",
        )
        return json.load(
            urllib.request.urlopen(req)
        )
    
    def _delete_data(self, url: str, params: dict):
        headers = self._get_base_header()
        headers["Content-Type"] = "application/json"
        return urllib.request.Request(
            url=url,
            headers=headers,
            data=json.dumps(params).encode("utf-8"),
            method="DELETE",
        )
    
    def _rename_field_code_from_jp_to_en(self, app_id: str, field_code: str):
        mappings = self.field_code_mappings[app_id]
        return mappings.get(field_code, field_code)
    
    def rename_app_name(self, app_id: str, app_name: str):
        mappings = self.app_name_mappings
        return mappings.get(app_id, app_name)

    # ref. https://kintone.dev/en/docs/kintone/rest-api/apps/get-app/
    def get_app(self, app_id: str):
        url = self._get_base_url() + "/k/v1/apps.json"
        params = {"ids": app_id}
        apps = self._fetch_data(url, params)
        return apps.get("apps")[0]

    # ref. https://kintone.dev/en/docs/kintone/rest-api/apps/get-form-fields/
    def get_app_fields(self, app_id: str):
        url = self._get_base_url() + "/k/v1/app/form/fields.json"
        params = {"app": app_id}
        res = self._fetch_data(url, params)
        fields = res["properties"]
        without_fields = ["カテゴリー", "作業者", "ステータス"]
        return {self._rename_field_code_from_jp_to_en(app_id, x): fields[x] for x in fields if x not in without_fields}

    # ref. https://kintone.dev/en/docs/kintone/rest-api/records/add-cursor/
    def create_cursor(self, app_id: str, cursor_field: str = None, cursor_value: str = None):
        params = {
            "app": app_id,
            "size": 500,
        }
        # https://cybozu.dev/ja/kintone/docs/overview/query/
        if cursor_field and cursor_value:
            params["query"] = f"{cursor_field} > \"{cursor_value}\""
        url = self._get_base_url() + "/k/v1/records/cursor.json"
        return self._post_data(url, params)

    def get_app_records(self, app_id: str, cursor_field: str = None, cursor_value: str = None):
        cursor = self.create_cursor(app_id, cursor_field, cursor_value)
        while True:
            records, next = self.get_records_by_cursor(app_id, cursor["id"])
            for record in records:
                yield record
            if next == False:
                self.delete_cursor(cursor["id"])
                break
            
        
    # ref. https://kintone.dev/en/docs/kintone/rest-api/records/get-cursor/
    def get_records_by_cursor(self, app_id: str, cursor_id: str):
        params = {
            "id": cursor_id,
        }
        url = self._get_base_url() + "/k/v1/records/cursor.json"
        res = self._fetch_data(url, params, True)
        records = []
        for record in res["records"]:
            item = {}
            for k, v in record.items():
                item[self._rename_field_code_from_jp_to_en(app_id, k)] = v["value"]

            records.append(item)

        return records, res["next"]

    # ref. https://kintone.dev/en/docs/kintone/rest-api/records/delete-cursor/
    def delete_cursor(self, cursor_id: str):
        params = {
            "id": cursor_id,
        }
        url = self._get_base_url() + "/k/v1/records/cursor.json"
        return self._delete_data(url, params)

    def get_stream(self, app_id: str):
        app = self.get_app(app_id)
        # https://jp.cybozu.help/k/en/user/app_settings/app_othersettings/appcode.html
        app_name_original = app.get("name")
        if not app_name_original:
            return None
        app_name = self.rename_app_name(app_id, app_name_original)

        json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {},
        }

        fields = self.get_app_fields(app_id)
        for k, _ in fields.items():
            # TODO: Implement more accurate type casting
            # https://kintone.dev/en/docs/kintone/overview/field-types/
            json_schema["properties"][k] = {"type": "string"}

        return AirbyteStream(
            name=app_name,
            json_schema=json_schema,
            supported_sync_modes=["full_refresh", "incremental"],
            #default_cursor_field=["update_date_time"],
        )

def update_url(url, params):
    url_parts = urllib.parse.urlparse(url)
    query = dict(urllib.parse.parse_qsl(url_parts.query))
    query.update(params)
    return url_parts._replace(query=urllib.parse.urlencode(query)).geturl()
