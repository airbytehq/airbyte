#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, Callable, Iterable, List, Mapping, MutableMapping, Tuple

Record = MutableMapping[str, Any]


def int_list(lst: Iterable[Any]) -> List[int]:
    return [int(item) for item in lst]


class APIResponseAdapter(ABC):
    def __init__(self, stream_name: str, api_endpoint: str):
        self.stream_name = stream_name
        self.api_endpoint = api_endpoint

    @property
    @abstractmethod
    def _deprecated_fields_by_stream(self) -> Mapping[str, Tuple[Tuple[str, Any], ...]]:
        pass

    @property
    @abstractmethod
    def _new_fields_by_stream(self) -> Mapping[str, Tuple[str, ...]]:
        pass

    @property
    @abstractmethod
    def _renamed_fields_by_stream(self) -> Mapping[str, Tuple[Tuple[str, str], ...]]:
        pass

    @property
    @abstractmethod
    def _type_changed_fields_by_stream(self) -> Mapping[str, Tuple[Tuple[str, Callable], ...]]:
        pass

    @property
    @abstractmethod
    def current_version(self):
        pass

    @property
    @abstractmethod
    def target_version(self):
        pass

    @staticmethod
    def field_by_name(record: Record, field: str) -> Tuple[MutableMapping[Any, Any], str]:
        path = field.split("/")
        container = record
        name = path.pop()
        for item in path:
            container = container.get(item, {})
        return container, name

    def find_mapping(self, attr) -> Iterable:
        mapping = attr.get(self.stream_name, ())
        return mapping or attr.get(self.api_endpoint, ())

    def _adjust_deprecated_fields(self, record: Record):
        for field_path, default_value in self.find_mapping(self._deprecated_fields_by_stream):
            container, field_name = self.field_by_name(record, field_path)
            container[field_name] = default_value

    def _adjust_new_fields(self, record: Record):
        for field_path in self.find_mapping(self._new_fields_by_stream):
            container, field_name = self.field_by_name(record, field_path)
            container.pop(field_name, None)

    def _adjust_renamed_fields(self, record: Record):
        for new_field_path, old_field_path in self.find_mapping(self._renamed_fields_by_stream):
            new_container, new_field_name = self.field_by_name(record, new_field_path)
            field_in_record = new_field_name in new_container
            if not field_in_record:
                continue
            old_container, old_field_name = self.field_by_name(record, old_field_path)
            old_container[old_field_name] = new_container.pop(new_field_name)

    def _adjust_type_changes(self, record: Record):
        for field_path, type_caster in self.find_mapping(self._type_changed_fields_by_stream):
            container, field_name = self.field_by_name(record, field_path)
            field_in_record = field_name in container
            if not field_in_record:
                continue
            value = container.pop(field_name)
            container[field_name] = value if value is None else type_caster(value)

    def adjust(self, record: Record):
        self._adjust_deprecated_fields(record)
        self._adjust_new_fields(record)
        self._adjust_renamed_fields(record)
        self._adjust_type_changes(record)


class v13_to_v12_adapter(APIResponseAdapter):
    current_version = "v1.3"
    target_version = "v1.2"

    _deprecated_fields_by_stream = {
        "ads": (
            ("premium_badge_id", None),
            ("tracking_pixel_id", None),
        ),
        "ad_groups": (("carriers", None),),
    }
    _new_fields_by_stream = {
        "ads": (
            "product_specific_type",
            "catalog_id",
            "item_group_ids",
            "product_set_id",
            "sku_ids",
            "dynamic_format",
            "vertical_video_strategy",
            "dynamic_destination",
        ),
        "ad_groups": ("shopping_ads_type", "product_source"),
        "reports/integrated/get/": ("X-Tt-Ads-Throttle",),
    }
    _renamed_fields_by_stream = {
        "ads": (
            ("secondary_status", "status"),
            ("operation_status", "opt_status"),
            ("profile_image_url", "profile_image"),
            ("deeplink", "open_url"),
            ("deeplink_type", "open_url_type"),
            ("vast_moat_enabled", "vast_moat"),
            ("creative_authorized", "is_creative_authorized"),
            ("shopping_ads_fallback_type", "dpa_fallback_type"),
            ("shopping_deeplink_type", "dpa_open_url_type"),
            ("shopping_ads_video_package_id", "dpa_video_tpl_id"),
        ),
        "advertisers": (("advertiser_id", "id"), ("rejection_reason", "reason"), ("cellphone_number", "phonenumber")),
        "campaigns": (
            ("budget_optimize_on", "budget_optimize_switch"),
            ("operation_status", "opt_status"),
            ("campaign_app_profile_page_state", "campaign_app_profile_page_type"),
            ("special_industries", "industry_types"),
            ("secondary_status", "status"),
            ("optimization_goal", "optimize_goal"),
        ),
        "ad_groups": (
            ("share_disabled", "is_share_disable"),
            ("placements", "placement"),
            ("inventory_filter_enabled", "enable_inventory_filter"),
            ("promotion_type", "external_type"),
            ("optimization_event", "external_action"),
            ("secondary_optimization_event", "deep_external_action"),
            ("age_groups", "age"),
            ("operating_systems", "operation_system"),
            ("network_types", "connection_type"),
            ("device_price_ranges", "device_price"),
            ("min_android_version", "android_osv"),
            ("ios14_targeting", "ios_target_device"),
            ("min_ios_version", "ios_osv"),
            ("optimization_goal", "optimize_goal"),
            ("bid_price", "bid"),
            ("conversion_bid_price", "conversion_bid"),
            ("deep_cpa_bid", "deep_cpabid"),
            ("next_day_retention", "daily_retention_ratio"),
            ("secondary_status", "status"),
            ("operation_status", "opt_status"),
            ("actions", "action_v2"),
            ("video_user_actions", "user_actions"),
            ("rf_purchased_type", "rf_buy_type"),
            ("purchased_impression", "buy_impression"),
            ("purchased_reach", "buy_reach"),
            ("rf_estimated_cpr", "rf_predict_cpr"),
            ("rf_estimated_frequency", "rf_predict_frequency"),
            ("included_custom_actions", "include_custom_actions"),
            ("excluded_custom_actions", "exclude_custom_actions"),
            ("shopping_ads_retargeting_type", "dpa_retargeting_type"),
            ("brand_safety_type", "brand_safety"),
            ("expansion_enabled", "enable_expansion"),
            ("adgroup_app_profile_page_state", "ad_app_profile_page_type"),
            ("delivery_mode", "display_mode"),
            ("comment_disabled", "is_comment_disable"),
            ("store_authorized_bc_id", "store_authorized_bc"),
            ("audience_ids", "audience"),
            ("excluded_audience_ids", "excluded_audience"),
            ("location_ids", "location"),
            ("interest_category_ids", "interest_category_v2"),
            ("interest_keyword_ids", "interest_keywords"),
            ("device_model_ids", "device_models"),
            ("carriers_ids", "carriers_v2"),
            ("video_download_disabled", "video_download"),
            ("blocked_pangle_app_ids", "pangle_block_app_list_id"),
            ("action_category_ids", "action_categories"),
            ("included_pangle_audience_package_ids", "pangle_audience_package_include"),
            ("excluded_pangle_audience_package_ids", "pangle_audience_package_exclude"),
            ("catalog_authorized_bc_id", "catalog_authorized_bc"),
            ("auto_targeting_enabled", "automated_targeting"),
        ),
        "reports/integrated/get/": (("metrics/placement_type", "metrics/placement"),),
    }
    _type_changed_fields_by_stream = {
        "ads": (
            ("advertiser_id", int),
            ("campaign_id", int),
            ("adgroup_id", int),
            ("ad_id", int),
            ("tiktok_item_id", int),
            ("card_id", int),
        ),
        "advertiser_ids": (("advertiser_id", int),),
        "advertisers": (("id", int),),
        "campaigns": (("budget_optimize_switch", int), ("campaign_ids", int), ("advertiser_id", int)),
        "ad_groups": (
            ("is_comment_disable", int),
            ("store_authorized_bc", int),
            ("audience", int_list),
            ("excluded_audience", int_list),
            ("location", int_list),
            ("interest_category_v2", int_list),
            ("interest_keywords", int_list),
            ("device_models", int_list),
            ("carriers_v2", int_list),
            ("video_download", str),
            ("pangle_block_app_list_id", int_list),
            ("action_categories", int_list),
            ("pangle_audience_package_include", int_list),
            ("pangle_audience_package_exclude", int_list),
            ("catalog_authorized_bc", int),
            ("automated_targeting", str),
            ("advertiser_id", int),
            ("campaign_id", int),
            ("adgroup_id", int),
            ("app_id", int),
            ("store_id", int),
            ("pixel_id", int),
            ("skip_learning_phase", int),
            ("catalog_id", int),
            ("product_set_id", int),
            ("schedule_id", int),
        ),
        "reports/integrated/get/": (
            ("dimensions/advertiser_id", int),
            ("metrics/campaign_id", int),
            ("dimensions/adgroup_id", int),
            ("dimensions/ad_id", int),
        ),
    }


class v14_to_v13_adapter(APIResponseAdapter):
    current_version = "v1.4"
    target_version = "v1.3"

    def adjust(self, record: Record):
        # a stub for the future
        pass


adapters = {adapter.current_version: adapter for adapter in (v13_to_v12_adapter, v14_to_v13_adapter)}


def get_response_adapter(current_version: str, target_version: str, stream_name: str, api_endpoint: str) -> Callable:
    def schema_adapter(class_chain: Callable) -> Callable:
        def adjust(record: Record):
            for cls in class_chain():
                cls.adjust(record)

        return adjust

    def chain() -> Iterable[APIResponseAdapter]:
        prev_version = current_version
        while target_version != prev_version:
            cls = adapters[prev_version]
            yield cls(stream_name, api_endpoint)
            prev_version = cls.target_version

    return schema_adapter(chain)
