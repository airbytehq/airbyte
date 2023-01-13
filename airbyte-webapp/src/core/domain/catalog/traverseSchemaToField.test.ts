import { AirbyteJSONSchema } from "core/jsonSchema/types";

import { traverseSchemaToField } from "./traverseSchemaToField";

describe(`${traverseSchemaToField}`, () => {
  it("traverses a nested schema", () => {
    const nestedSchema: AirbyteJSONSchema = {
      $schema: "http://json-schema.org/draft-04/schema#",
      type: "object",
      properties: {
        "1": {
          type: "object",
          properties: {
            "1_1": {
              type: "object",
              properties: {
                "1_1_1": {
                  type: "boolean",
                },
              },
              required: ["1_1_1"],
            },
          },
          required: ["1_1"],
        },
      },
    };
    const expected = [
      {
        airbyte_type: undefined,
        cleanedName: "1",
        fields: [
          {
            airbyte_type: undefined,
            cleanedName: "1_1",
            fields: [
              {
                airbyte_type: undefined,
                cleanedName: "1_1_1",
                fields: undefined,
                format: undefined,
                key: "1_1_1",
                path: ["1", "1_1", "1_1_1"],
                type: "boolean",
              },
            ],
            format: undefined,
            key: "1_1",
            path: ["1", "1_1"],
            type: "object",
          },
        ],
        format: undefined,
        key: "1",
        path: ["1"],
        type: "object",
      },
    ];
    expect(traverseSchemaToField(nestedSchema, "test_stream")).toEqual(expected);
  });

  it("traverses a flat schema", () => {
    const flatSchema: AirbyteJSONSchema = {
      $schema: "http://json-schema.org/draft-04/schema#",
      type: "object",
      properties: {
        "1": {
          type: "boolean",
        },
        "2": {
          type: "boolean",
        },
        "3": {
          type: "boolean",
        },
      },
    };
    const expected = [
      {
        airbyte_type: undefined,
        cleanedName: "1",
        type: "boolean",
        format: undefined,
        key: "1",
        path: ["1"],
      },
      {
        airbyte_type: undefined,
        cleanedName: "2",
        type: "boolean",
        format: undefined,
        key: "2",
        path: ["2"],
      },
      {
        airbyte_type: undefined,
        cleanedName: "3",
        type: "boolean",
        format: undefined,
        key: "3",
        path: ["3"],
      },
    ];
    expect(traverseSchemaToField(flatSchema, "test_stream")).toEqual(expected);
  });
});
