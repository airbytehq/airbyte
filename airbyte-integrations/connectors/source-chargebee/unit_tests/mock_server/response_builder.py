# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from http import HTTPStatus
from pathlib import Path

from airbyte_cdk.test.mock_http import HttpResponse


def _get_response_path() -> Path:
    """Get path to response JSON files."""
    return Path(__file__).parent.parent / "resource" / "http" / "response"


def get_json_response(filename: str) -> str:
    """Load a JSON response from the resource directory."""
    response_path = _get_response_path() / filename
    return response_path.read_text()


def json_response(filename: str, status_code: HTTPStatus = HTTPStatus.OK) -> HttpResponse:
    """Create an HttpResponse from a JSON file."""
    body = get_json_response(filename)
    return HttpResponse(body=body, status_code=status_code.value, headers={})


def customer_response() -> HttpResponse:
    """Customer stream response."""
    return json_response("customer.json")


def customer_response_page1() -> HttpResponse:
    """Customer stream response - page 1 with next_offset."""
    return json_response("customer_page1.json")


def customer_response_page2() -> HttpResponse:
    """Customer stream response - page 2 (last page)."""
    return json_response("customer_page2.json")


def customer_response_multiple() -> HttpResponse:
    """Customer stream response with multiple records."""
    return json_response("customer_multiple.json")


def subscription_response() -> HttpResponse:
    """Subscription stream response."""
    return json_response("subscription.json")


def subscription_response_page1() -> HttpResponse:
    """Subscription stream response - page 1 with next_offset."""
    return json_response("subscription_page1.json")


def subscription_response_page2() -> HttpResponse:
    """Subscription stream response - page 2 (last page)."""
    return json_response("subscription_page2.json")


def invoice_response() -> HttpResponse:
    """Invoice stream response."""
    return json_response("invoice.json")


def event_response() -> HttpResponse:
    """Event stream response."""
    return json_response("event.json")


def event_response_page1() -> HttpResponse:
    """Event stream response - page 1 with next_offset."""
    return json_response("event_page1.json")


def event_response_page2() -> HttpResponse:
    """Event stream response - page 2 (last page)."""
    return json_response("event_page2.json")


def transaction_response() -> HttpResponse:
    """Transaction stream response."""
    return json_response("transaction.json")


def plan_response() -> HttpResponse:
    """Plan stream response."""
    return json_response("plan.json")


def addon_response() -> HttpResponse:
    """Addon stream response."""
    return json_response("addon.json")


def coupon_response() -> HttpResponse:
    """Coupon stream response."""
    return json_response("coupon.json")


def credit_note_response() -> HttpResponse:
    """Credit note stream response."""
    return json_response("credit_note.json")


def gift_response() -> HttpResponse:
    """Gift stream response."""
    return json_response("gift.json")


def item_response() -> HttpResponse:
    """Item stream response."""
    return json_response("item.json")


def item_response_multiple() -> HttpResponse:
    """Item stream response with multiple records."""
    return json_response("item_multiple.json")


def contact_response() -> HttpResponse:
    """Contact stream response (substream of customer)."""
    return json_response("contact.json")


def attached_item_response() -> HttpResponse:
    """Attached item stream response (substream of item)."""
    return json_response("attached_item.json")


def empty_response() -> HttpResponse:
    """Empty response with no records."""
    return json_response("empty.json")


def error_response(status_code: HTTPStatus = HTTPStatus.UNAUTHORIZED) -> HttpResponse:
    """Error response for testing error handling."""
    error_files = {
        HTTPStatus.UNAUTHORIZED: "error_unauthorized.json",
        HTTPStatus.NOT_FOUND: "error_not_found.json",
    }
    filename = error_files.get(status_code, "error_unauthorized.json")
    return json_response(filename, status_code)


def configuration_incompatible_response() -> HttpResponse:
    """Response for configuration_incompatible error (IGNORE action)."""
    return json_response("error_configuration_incompatible.json", HTTPStatus.BAD_REQUEST)


def order_response() -> HttpResponse:
    """Order stream response."""
    return json_response("order.json")


def hosted_page_response() -> HttpResponse:
    """Hosted page stream response."""
    return json_response("hosted_page.json")


def item_price_response() -> HttpResponse:
    """Item price stream response."""
    return json_response("item_price.json")


def payment_source_response() -> HttpResponse:
    """Payment source stream response."""
    return json_response("payment_source.json")


def promotional_credit_response() -> HttpResponse:
    """Promotional credit stream response."""
    return json_response("promotional_credit.json")


def subscription_response_multiple() -> HttpResponse:
    """Subscription stream response with multiple records."""
    return json_response("subscription_multiple.json")


def subscription_with_scheduled_changes_response() -> HttpResponse:
    """Subscription with scheduled changes stream response."""
    return json_response("subscription_with_scheduled_changes.json")


def unbilled_charge_response() -> HttpResponse:
    """Unbilled charge stream response."""
    return json_response("unbilled_charge.json")


def virtual_bank_account_response() -> HttpResponse:
    """Virtual bank account stream response."""
    return json_response("virtual_bank_account.json")


def quote_response() -> HttpResponse:
    """Quote stream response."""
    return json_response("quote.json")


def quote_response_multiple() -> HttpResponse:
    """Quote stream response with multiple records."""
    return json_response("quote_multiple.json")


def quote_line_group_response() -> HttpResponse:
    """Quote line group stream response."""
    return json_response("quote_line_group.json")


def site_migration_detail_response() -> HttpResponse:
    """Site migration detail stream response."""
    return json_response("site_migration_detail.json")


def comment_response() -> HttpResponse:
    """Comment stream response."""
    return json_response("comment.json")


def item_family_response() -> HttpResponse:
    """Item family stream response."""
    return json_response("item_family.json")


def differential_price_response() -> HttpResponse:
    """Differential price stream response."""
    return json_response("differential_price.json")


def error_no_scheduled_changes_response() -> HttpResponse:
    """Response for 'No changes are scheduled for this subscription' error (IGNORE action)."""
    return json_response("error_no_scheduled_changes.json", HTTPStatus.BAD_REQUEST)
