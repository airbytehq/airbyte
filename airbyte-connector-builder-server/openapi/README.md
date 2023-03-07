# OpenAPI templates
This directory contains custom OpenAPI templates used to generate Python code for the FastAPI. 

**But why?**

At the time we made this service (Nov 2022), no OSS OpenAPI generators enabled spec-first development. So we made these custom templates.

For the full context, see: https://github.com/airbytehq/airbyte/issues/17813

## How we're using templates
At a high level, the expected usage pattern for these templates is to generate code using the `python-fastapi` OpenAPI generator, then copy the `models` module and the `apis` into your project. This flow should work continuously i.e: as your spec evolves, it is safe to re-do this operation. 

The only change we're making to `python-fastapi` is to define an abstract class `AbstractApi` in which every method corresponds to an API endpoint. The developer is expected to extend the class and use that to instantiate the `APIRouter` provided to FastAPI. 

The existing `python-fastapi` OpenAPI generator does a pretty good job generating Pydantic models for entities declared in the OpenAPI spec, so we take those as-is. 

## Making changes to the templates
Please make sure you are at least familiar with the [User-defined Templates](https://openapi-generator.tech/docs/customization#user-defined-templates) section of the OpenAPI docs before you start iterating. 

Relevant OpenAPI docs: 
- https://openapi-generator.tech/docs/customization
- https://openapi-generator.tech/docs/templating
- https://openapi-generator.tech/docs/debugging

Happy templating!
