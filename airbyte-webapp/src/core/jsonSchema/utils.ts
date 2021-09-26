import { JSONSchema7, JSONSchema7Definition } from "json-schema";

function removeNestedPaths(
  schema: JSONSchema7Definition,
  pathList: string[][]
): JSONSchema7 {
  if (typeof schema === "boolean") {
    return null as any;
  }

  if (pathList.length === 0) {
    return schema;
  }

  const resultSchema: JSONSchema7 = schema;

  const oneOf = schema.oneOf;
  if (oneOf) {
    resultSchema.oneOf = oneOf.map((o) => removeNestedPaths(o, pathList));
  }

  const properties = schema.properties;
  if (properties) {
    const filteredProperties: Record<string, JSONSchema7Definition> = {};

    for (const propertiesKey in properties) {
      const matchingPaths = pathList.filter(([p]) => p === propertiesKey);

      if (matchingPaths.length === 0) {
        filteredProperties[propertiesKey] = properties[propertiesKey];
      }

      if (matchingPaths.some((p) => p.length === 1)) {
        if (schema.required) {
          resultSchema.required = schema.required?.filter(
            (requiredFiled) => requiredFiled !== propertiesKey
          );
        }
      } else {
        const innerPath = matchingPaths.map(([, ...rest]) => rest);

        filteredProperties[propertiesKey] = removeNestedPaths(
          properties[propertiesKey],
          innerPath
        );
      }
      resultSchema.properties = filteredProperties;
    }
  }

  return resultSchema;
}

export { removeNestedPaths };
