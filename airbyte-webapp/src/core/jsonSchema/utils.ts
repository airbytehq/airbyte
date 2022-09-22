import { JSONSchema7, JSONSchema7Definition } from "json-schema";

import { isDefined } from "utils/common";

import { AirbyteJSONSchema, AirbyteJSONSchemaDefinition } from "./types";

function removeNestedPaths(
  schema: AirbyteJSONSchemaDefinition,
  pathList: string[][],
  ignoreProp = true
): AirbyteJSONSchema {
  if (typeof schema === "boolean") {
    // TODO: Types need to be corrected here
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    return null as any;
  }

  if (pathList.length === 0) {
    return schema;
  }

  const resultSchema: JSONSchema7 = schema;

  if (schema.oneOf) {
    resultSchema.oneOf = schema.oneOf.map((o) => removeNestedPaths(o, pathList, ignoreProp));
  }

  if (schema.properties) {
    const { properties } = schema;
    const filteredProperties: Record<string, JSONSchema7Definition> = {};

    for (const propertiesKey in properties) {
      const matchingPaths = pathList.filter(([p]) => p === propertiesKey);

      if (matchingPaths.length === 0) {
        filteredProperties[propertiesKey] = properties[propertiesKey];
      }

      if (matchingPaths.some((p) => p.length === 1)) {
        if (schema.required) {
          resultSchema.required = schema.required?.filter((requiredFiled) => requiredFiled !== propertiesKey);
        }

        if (!ignoreProp) {
          const prop = properties[propertiesKey];
          if (typeof prop !== "boolean") {
            prop.airbyte_hidden = true;
          }
          filteredProperties[propertiesKey] = prop;
        }
      } else {
        const innerPath = matchingPaths.map(([, ...rest]) => rest);

        filteredProperties[propertiesKey] = removeNestedPaths(properties[propertiesKey], innerPath, ignoreProp);
      }
    }

    resultSchema.properties = filteredProperties;
  }

  return resultSchema;
}

function applyFuncAt(
  schema: JSONSchema7Definition,
  path: Array<string | number>,
  f: (schema: JSONSchema7Definition) => JSONSchema7
): JSONSchema7Definition {
  if (typeof schema === "boolean") {
    return schema;
  }

  const [pathElem, ...restPath] = path;

  if (!isDefined(pathElem)) {
    return f(schema);
  }

  const resultSchema: JSONSchema7 = schema;

  if (schema.oneOf) {
    const idx = typeof pathElem === "number" ? pathElem : parseInt(pathElem);
    resultSchema.oneOf = schema.oneOf.map((o, index) => (index === idx ? applyFuncAt(o, restPath, f) : o));
  }

  if (schema.properties && typeof pathElem === "string") {
    resultSchema.properties = Object.fromEntries(
      Object.entries(schema.properties).map(([key, value]) => [
        key,
        key === pathElem ? applyFuncAt(value, restPath, f) : value,
      ])
    );
  }

  return resultSchema;
}

export { applyFuncAt, removeNestedPaths };
