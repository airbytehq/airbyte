def get_base_api_url(subdomain: str) -> str:
    return f"{get_base_url(subdomain)}api/sunshine/"


def get_base_url(subdomain: str) -> str:
    return f"https://{subdomain}.zendesk.com/"
