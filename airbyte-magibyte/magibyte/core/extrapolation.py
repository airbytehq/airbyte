from jinja2 import Template


def extrapolate(input_str, context):
    return Template(input_str).render(context=context)
