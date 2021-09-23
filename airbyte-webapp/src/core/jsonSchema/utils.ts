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

  const { properties, ...restschema } = schema;

  const resultSchema: JSONSchema7 = restschema;
  if (properties) {
    const filteredProperties: Record<string, JSONSchema7Definition> = {};

    for (const propertiesKey in properties) {
      const matchingPaths = pathList.filter(([p]) => p === propertiesKey);

      if (matchingPaths.length === 0) {
        filteredProperties[propertiesKey] = properties[propertiesKey];
      }

      if (matchingPaths.some((p) => p.length === 1)) {
        // this path is excluded. No need to deep dive
      } else {
        const innerPath = matchingPaths.map(([, ...rest]) => rest);

        filteredProperties[propertiesKey] = removeNestedPaths(
          properties[propertiesKey],
          innerPath
        );
      }
    }

    resultSchema.properties = filteredProperties;
  }

  return resultSchema;
}

export { removeNestedPaths };
