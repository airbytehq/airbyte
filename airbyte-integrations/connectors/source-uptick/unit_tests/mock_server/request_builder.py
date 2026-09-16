# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any

from airbyte_cdk.test.mock_http import HttpRequest


class UptickRequestBuilder:
    """Build exact Uptick requests used by manifest-only stream tests."""

    BASE_URL = "https://test-tenant.onuptick.com"
    ACCESS_TOKEN = "tok"
    START_DATE = "2000-01-01T00:00:00.000000+0000"
    FIELDS = {
        "creditnotelineitems": (
            "CreditNoteLineItem",
            "id,created,updated,deleted,account_code,description,unit_price,quantity,subtotal,tax,total,taxcode,taxrate,creditnote,product",
        ),
        "defectquotelineitems": (
            "DefectQuoteLineItem",
            "id,created,updated,description,unit_price,cost_price,markup,quantity,taxcode,taxrate,subtotal,total,gst,index,estimated_time,product,quote,asset,remark",
        ),
        "remarkevents": (
            "RemarkEvent",
            "id,created,updated,event,notes,remark,task,servicetask,account",
        ),
        "majorservices": (
            "MajorService",
            "id,created,updated,asset,routineserviceleveltype,due,status",
        ),
        "promptquestions": (
            "PromptQuestion",
            "id,created,updated,deleted,label,type,ref,order,config,section",
        ),
        "promptanswers": (
            "PromptAnswer",
            "id,created,updated,value,question,answergroup,performed_date,guid",
        ),
        "servicequotefixedlineitems": (
            "ServiceLineItem",
            "id,servicequote,description,quantity,unit_price,billingcontract_type,index,estimated_duration,taxcode,taxrate,annual_tax,annual_subtotal,created,updated",
        ),
        "servicequotedoandchargelineitems": (
            "ServiceLineItem",
            "id,servicequote,description,quantity,unit_price,billingcontract_type,index,estimated_duration,taxcode,taxrate,annual_tax,site_price,annual_subtotal,service_price,created,updated",
        ),
    }

    @classmethod
    def token_endpoint(cls) -> str:
        return f"{cls.BASE_URL}/api/oauth2/token/"

    @classmethod
    def collection(cls, stream: str, page: int = 1) -> HttpRequest:
        model, fields = cls.FIELDS[stream]
        query_params: dict[str, Any] = {
            "ordering": "-updated",
            "show_deleted": "true",
            f"fields[{model}]": fields,
            "updatedsince": cls.START_DATE,
        }
        if page > 1:
            query_params["page"] = str(page)
        return HttpRequest(
            url=f"{cls.BASE_URL}/api/v2.15/{stream}/",
            query_params=query_params,
            headers={"Authorization": f"Bearer {cls.ACCESS_TOKEN}"},
        )

    @classmethod
    def next_page_url(cls, stream: str) -> str:
        return f"{cls.BASE_URL}/api/v2.15/{stream}/?page=2"
