from airbyte_cdk.sources.utils.casing import camel_to_snake

def deep_snake_keys(d):
    return {camel_to_snake(k): deep_snake_keys(v) if isinstance(v, dict) else v for k, v in d.items()}
