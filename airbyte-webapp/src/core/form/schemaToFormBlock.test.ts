import { FormGroupItem } from "core/form/types";
import { AirbyteJSONSchemaDefinition } from "core/jsonSchema/types";

import { jsonSchemaToFormBlock } from "./schemaToFormBlock";

it("should reformat jsonSchema to internal widget representation", () => {
  const schema: AirbyteJSONSchemaDefinition = {
    type: "object",
    required: ["host", "port", "user", "dbname"],
    properties: {
      host: { type: "string", description: "Hostname of the database." },
      port: {
        type: "integer",
        description: "Port of the database.",
      },
      user: {
        type: "string",
        description: "Username to use to access the database.",
      },
      dbname: { type: "string", description: "Name of the database." },
      password: {
        airbyte_secret: true,
        type: "string",
        description: "Password associated with the username.",
      },
    },
  };

  const builtSchema = jsonSchemaToFormBlock(schema, "key");

  const expected = {
    _type: "formGroup",
    path: "key",
    fieldKey: "key",
    isRequired: false,
    properties: [
      {
        _type: "formItem",
        description: "Hostname of the database.",
        path: "key.host",
        fieldKey: "host",
        isRequired: true,
        isSecret: false,
        multiline: false,
        type: "string",
      },
      {
        _type: "formItem",
        description: "Port of the database.",
        path: "key.port",
        fieldKey: "port",
        isRequired: true,
        isSecret: false,
        multiline: false,
        type: "integer",
      },
      {
        _type: "formItem",
        description: "Username to use to access the database.",
        path: "key.user",
        fieldKey: "user",
        isRequired: true,
        isSecret: false,
        multiline: false,
        type: "string",
      },
      {
        _type: "formItem",
        description: "Name of the database.",
        path: "key.dbname",
        fieldKey: "dbname",
        isRequired: true,
        isSecret: false,
        multiline: false,
        type: "string",
      },
      {
        _type: "formItem",
        description: "Password associated with the username.",
        path: "key.password",
        fieldKey: "password",
        isRequired: false,
        isSecret: true,
        multiline: false,
        type: "string",
      },
    ],
  };

  expect(builtSchema).toEqual(expected);
});

it("should turn single enum into const but keep multi value enum", () => {
  const schema: AirbyteJSONSchemaDefinition = {
    type: "object",
    required: ["a", "b", "c"],
    properties: {
      a: { type: "string", enum: ["val1", "val2"] },
      b: { type: "string", enum: ["val1"], default: "val1" },
      c: { type: "string", const: "val3" },
    },
  };

  const builtSchema = jsonSchemaToFormBlock(schema, "key");

  const expectedProperties = [
    {
      _type: "formItem",
      enum: ["val1", "val2"],
      fieldKey: "a",
      isRequired: true,
      isSecret: false,
      multiline: false,
      path: "key.a",
      type: "string",
    },
    {
      _type: "formItem",
      const: "val1",
      default: "val1",
      fieldKey: "b",
      isRequired: true,
      isSecret: false,
      multiline: false,
      path: "key.b",
      type: "string",
    },
    {
      _type: "formItem",
      const: "val3",
      fieldKey: "c",
      isRequired: true,
      isSecret: false,
      multiline: false,
      path: "key.c",
      type: "string",
    },
  ];
  expect((builtSchema as FormGroupItem).properties).toEqual(expectedProperties);
});

it("should reformat jsonSchema to internal widget representation with parent schema", () => {
  const schema: AirbyteJSONSchemaDefinition = {
    type: "object",
    title: "Postgres Source Spec",
    required: ["host", "port", "user", "dbname"],
    properties: {
      host: { type: "string", description: "Hostname of the database." },
    },
  };

  const builtSchema = jsonSchemaToFormBlock(schema, "key", undefined, {
    required: ["key"],
  });

  const expected = {
    _type: "formGroup",
    fieldKey: "key",
    path: "key",
    isRequired: true,
    properties: [
      {
        _type: "formItem",
        description: "Hostname of the database.",
        fieldKey: "host",
        path: "key.host",
        isRequired: true,
        isSecret: false,
        multiline: false,
        type: "string",
      },
    ],
    title: "Postgres Source Spec",
  };

  expect(builtSchema).toEqual(expected);
});

it("should reformat jsonSchema to internal widget representation when has oneOf", () => {
  const schema: AirbyteJSONSchemaDefinition = {
    type: "object",
    required: ["start_date", "credentials"],
    properties: {
      start_date: {
        type: "string",
      },
      credentials: {
        type: "object",
        title: "Credentials Condition",
        description: "Credentials Condition Description",
        order: 0,
        oneOf: [
          {
            title: "api key",
            required: ["api_key"],
            properties: {
              api_key: {
                type: "string",
              },
              type: {
                type: "string",
                const: "api",
                default: "api",
              },
            },
          },
          {
            title: "oauth",
            required: ["redirect_uri"],
            properties: {
              redirect_uri: {
                type: "string",
                examples: ["https://api.hubspot.com/"],
              },
              type: {
                type: "string",
                const: "oauth",
                default: "oauth",
              },
            },
          },
        ],
      },
    },
  };

  const builtSchema = jsonSchemaToFormBlock(schema, "key", undefined, {
    required: ["key"],
  });

  const expected = {
    _type: "formGroup",
    path: "key",
    fieldKey: "key",
    properties: [
      {
        _type: "formItem",
        path: "key.start_date",
        fieldKey: "start_date",
        isRequired: true,
        isSecret: false,
        multiline: false,
        type: "string",
      },
      {
        _type: "formCondition",
        path: "key.credentials",
        description: "Credentials Condition Description",
        title: "Credentials Condition",
        order: 0,
        fieldKey: "credentials",
        selectionConstValues: ["api", "oauth"],
        selectionKey: "type",
        selectionPath: "key.credentials.type",
        conditions: [
          {
            title: "api key",
            _type: "formGroup",
            path: "key.credentials",
            fieldKey: "credentials",
            properties: [
              {
                _type: "formItem",
                path: "key.credentials.api_key",
                fieldKey: "api_key",
                isRequired: true,
                isSecret: false,
                multiline: false,
                type: "string",
              },
              {
                _type: "formItem",
                const: "api",
                default: "api",
                fieldKey: "type",
                format: undefined,
                isRequired: false,
                isSecret: false,
                multiline: false,
                path: "key.credentials.type",
                type: "string",
              },
            ],
            isRequired: false,
          },
          {
            title: "oauth",
            _type: "formGroup",
            path: "key.credentials",
            fieldKey: "credentials",
            properties: [
              {
                examples: ["https://api.hubspot.com/"],
                _type: "formItem",
                path: "key.credentials.redirect_uri",
                fieldKey: "redirect_uri",
                isRequired: true,
                isSecret: false,
                multiline: false,
                type: "string",
              },
              {
                _type: "formItem",
                const: "oauth",
                default: "oauth",
                fieldKey: "type",
                format: undefined,
                isRequired: false,
                isSecret: false,
                multiline: false,
                path: "key.credentials.type",
                type: "string",
              },
            ],
            isRequired: false,
          },
        ],
        isRequired: true,
      },
    ],
    isRequired: true,
  };

  expect(builtSchema).toEqual(expected);
});
