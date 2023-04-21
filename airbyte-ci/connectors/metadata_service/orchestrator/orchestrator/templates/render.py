from jinja2 import Environment, PackageLoader


def render_connector_registry_locations_html(destinations_table: str, sources_table: str) -> str:
    env = Environment(loader=PackageLoader("orchestrator", "templates"))
    template = env.get_template("connector_registry_locations.html")
    return template.render(destinations_table=destinations_table, sources_table=sources_table)
