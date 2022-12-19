import { FormGroupItem } from "core/form/types";

import { jsonSchemaToUiWidget } from "./schemaToUiWidget";
import { AirbyteJSONSchemaDefinition } from "./types";

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

  const builtSchema = jsonSchemaToUiWidget(schema, "key");

  const expected = {
    _type: "formGroup",
    path: "key",
    fieldKey: "key",
    isRequired: false,
    jsonSchema: {
      properties: {
        dbname: {
          description: "Name of the database.",
          type: "string",
        },
        host: {
          description: "Hostname of the database.",
          type: "string",
        },
        password: {
          airbyte_secret: true,
          description: "Password associated with the username.",
          type: "string",
        },
        port: {
          description: "Port of the database.",
          type: "integer",
        },
        user: {
          description: "Username to use to access the database.",
          type: "string",
        },
      },
      required: ["host", "port", "user", "dbname"],
      type: "object",
    },
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

  const builtSchema = jsonSchemaToUiWidget(schema, "key");

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

  const builtSchema = jsonSchemaToUiWidget(schema, "key", undefined, {
    required: ["key"],
  });

  const expected = {
    _type: "formGroup",
    fieldKey: "key",
    path: "key",
    isRequired: true,
    jsonSchema: {
      properties: {
        host: {
          description: "Hostname of the database.",
          type: "string",
        },
      },
      required: ["host", "port", "user", "dbname"],
      title: "Postgres Source Spec",
      type: "object",
    },
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
            },
          },
        ],
      },
    },
  };

  const builtSchema = jsonSchemaToUiWidget(schema, "key", undefined, {
    required: ["key"],
  });

  const expected = {
    _type: "formGroup",
    jsonSchema: {
      type: "object",
      required: ["start_date", "credentials"],
      properties: {
        start_date: { type: "string" },
        credentials: {
          type: "object",
          description: "Credentials Condition Description",
          title: "Credentials Condition",
          order: 0,
          oneOf: [
            {
              title: "api key",
              required: ["api_key"],
              properties: { api_key: { type: "string" } },
            },
            {
              title: "oauth",
              required: ["redirect_uri"],
              properties: {
                redirect_uri: {
                  type: "string",
                  examples: ["https://api.hubspot.com/"],
                },
              },
            },
          ],
        },
      },
    },
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
        conditions: {
          "api key": {
            title: "api key",
            _type: "formGroup",
            jsonSchema: {
              title: "api key",
              required: ["api_key"],
              type: "object",
              properties: { api_key: { type: "string" } },
            },
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
            ],
            isRequired: false,
          },
          oauth: {
            title: "oauth",
            _type: "formGroup",
            jsonSchema: {
              title: "oauth",
              required: ["redirect_uri"],
              type: "object",
              properties: {
                redirect_uri: {
                  type: "string",
                  examples: ["https://api.hubspot.com/"],
                },
              },
            },
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
            ],
            isRequired: false,
          },
        },
        isRequired: true,
      },
    ],
    isRequired: true,
  };

  expect(builtSchema).toEqual(expected);
});
