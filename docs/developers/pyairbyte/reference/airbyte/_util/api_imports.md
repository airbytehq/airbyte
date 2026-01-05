---
sidebar_label: api_imports
title: airbyte._util.api_imports
---

Imported classes from the Airbyte API.

Any classes that are imported from the Airbyte API should be imported here.
This allows for easy access to these classes in other modules, especially
for type hinting purposes.

Design Guidelines:
- No modules except `api_util` and `api_imports` should import from `airbyte_api`.
- If a module needs to import from `airbyte_api`, it should import from `api_imports` (this module)
  instead.
- This module is divided into two sections: internal-use classes and public-use classes.
- Public-use classes should be carefully reviewed to ensure that they are necessary for public use
  and that we are willing to support them as part of PyAirbyte.

## annotations

## ConnectionResponse

## DestinationResponse

## JobResponse

## JobStatusEnum

#### \_\_all\_\_

