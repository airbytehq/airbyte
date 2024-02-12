from typing import Optional, Union

from pydantic import BaseModel

from source_ozon.schemas.banner_report_data import BannerReport
from source_ozon.schemas.brend_shelf_report_data import BrandShelfReport
from source_ozon.schemas.search_promo_report_data import SearchPromoReport
from source_ozon.schemas.sku_report_data import SkuReport


class OzonCampaign(BaseModel):
    id: str
    title: str
    advObjectType: str
    date: Optional[str]


class CampaignReport(BaseModel):
    campaign_id: str
    campaign_name: str
    campaign_type: str
    report_data: Optional[Union[SearchPromoReport, BannerReport, BrandShelfReport, SkuReport]]
