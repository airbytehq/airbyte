import { JSONSchema7Definition } from "json-schema";
import Status from "core/statuses";
import { NetworkError } from "core/request/NetworkError";
import { SourceDiscoverSchemaRead } from "./api";
import { SyncSchemaField } from "./models";

// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
export function toInnerModel(
  result: SourceDiscoverSchemaRead
): SourceDiscoverSchemaRead {
  if (result.jobInfo?.status === Status.FAILED || !result.catalog) {
    // @ts-ignore address this case
    const e = new NetworkError(result);
    // Generate error with failed status and received logs
    e.status = 400;
    // @ts-ignore address this case
    e.response = result.jobInfo;
    throw e;
  }

  return result;
}

export const traverseSchemaToField = (
  jsonSchema: JSONSchema7Definition,
  key: string
): SyncSchemaField[] => {
  // For the top level we should not insert an extra object
  return traverseJsonSchemaProperties(jsonSchema, key)[0].fields ?? [];
};

const traverseJsonSchemaProperties = (
  jsonSchema: JSONSchema7Definition,
  key: string,
  path: string = key
): SyncSchemaField[] => {
  if (typeof jsonSchema === "boolean") {
    return [];
  }

  let fields: SyncSchemaField[] | undefined;
  if (jsonSchema.properties) {
    fields = Object.entries(jsonSchema.properties)
      .flatMap(([k, schema]) =>
        traverseJsonSchemaProperties(schema, k, `${path}.${k}`)
      )
      .flat(2);
  }

  return [
    {
      cleanedName: key,
      name: path || key,
      key,
      fields,
      type:
        (Array.isArray(jsonSchema.type)
          ? jsonSchema.type.find((t) => t !== "null") ?? jsonSchema.type[0]
          : jsonSchema.type) ?? "null",
    },
  ];
};
