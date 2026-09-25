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
        "tasks": (
            "Task",
            "id,created,updated,deleted,ref,description,is_active,inactive_date,extra_fields,due,due_after,pm_date,tolerance_start,tolerance_end,invoiced_date,name,scope_of_works,address,coord_lat,coord_lng,access_note,access_window,access_procedure,access_schedule,access_code,internal_note,workorder_url,technician_note,partner_uid,priority,sla_incident_notification_at,sla_due_inprogress,sla_due_inspected,charge_type,notes,invoice_note,estimated_duration,authorisation_name,authorisation_note,authorisation_ref,authorisation_amount,authorisation_date,contractor_note,status_changed_inprogress,status_changed_inspected,status_changed_complete,app_link,timezone,bulk_email_last_sent_at,contractor_authorisation_limit,category,servicegroup,client,property,billingcard,assigned_to,assigned_office,salesperson,technician,round,tags,branch,supporting_technicians,costcentre,parent_task,author,contractor,contractor_assigned_technician,updated_by,status,zone,required_accreditationtypes,project,sla,callout",
        ),
        "servicegroups": (
            "ServiceGroup",
            "id,created,updated,name",
        ),
        "accreditationtypes": (
            "AccreditationType",
            "id,created,updated,name,type,property_specific,extra_fields",
        ),
    }

    @classmethod
    def token_endpoint(cls) -> str:
        return f"{cls.BASE_URL}/api/oauth2/token/"

    @classmethod
    def collection(
        cls,
        stream: str,
        page: int = 1,
        updatedsince: str = START_DATE,
        token: str = ACCESS_TOKEN,
    ) -> HttpRequest:
        model, fields = cls.FIELDS[stream]
        query_params: dict[str, Any] = {
            "ordering": "-updated",
            "show_deleted": "true",
            f"fields[{model}]": fields,
            "updatedsince": updatedsince,
        }
        if page > 1:
            query_params["page"] = str(page)
        return HttpRequest(
            url=f"{cls.BASE_URL}/api/v2.15/{stream}/",
            query_params=query_params,
            headers={"Authorization": f"Bearer {token}"},
        )

    @classmethod
    def next_page_url(cls, stream: str) -> str:
        return f"{cls.BASE_URL}/api/v2.15/{stream}/?page=2"
