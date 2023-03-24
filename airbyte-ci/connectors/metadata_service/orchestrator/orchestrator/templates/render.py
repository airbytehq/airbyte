from jinja2 import Environment, PackageLoader


def render_connector_catalog_locations_html(destinations_table: str, sources_table: str) -> str:
    env = Environment(loader=PackageLoader("orchestrator", "templates"))
    template = env.get_template("connector_catalog_locations.html")
    return template.render(destinations_table=destinations_table, sources_table=sources_table)


def render_connector_catalog_locations_markdown(destinations_markdown: str, sources_markdown: str) -> str:
    env = Environment(loader=PackageLoader("orchestrator", "templates"))
    template = env.get_template("connector_catalog_locations.md")
    return template.render(destinations_markdown=destinations_markdown, sources_markdown=sources_markdown)
