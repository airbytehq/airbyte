import { JSONSchema7Definition } from "json-schema";
import Status from "core/statuses";
import { NetworkError } from "core/resources/BaseResource";
import { SourceDiscoverSchemaRead } from "./api";
import { SyncSchemaField } from "./models";

export function toInnerModel(result: any): SourceDiscoverSchemaRead {
  if (result.jobInfo?.job?.status === Status.FAILED || !result.catalog) {
    const e = new NetworkError(result);
    // Generate error with failed status and received logs
    e.status = 400;
    e.response = result.jobInfo;
    throw e;
  }

  return result;
}

export const traverseSchemaToField = (
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
        traverseSchemaToField(schema, k, `${path}.${k}`)
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
          ? jsonSchema.type.find(t => t !== "null") ?? jsonSchema.type[0]
          : jsonSchema.type) ?? "null"
    }
  ];
};
