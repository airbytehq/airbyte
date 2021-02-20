import { JSONSchema7 } from "json-schema";

import { jsonSchemaToUiWidget } from "./schemaToUiWidget";

test("should reformat jsonSchema to internal widget representation", () => {
  const schema: JSONSchema7 = {
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
      } as any, // Because airbyte_secret is not part of json_schema
    },
  };

  const builtSchema = jsonSchemaToUiWidget(schema, "key");

  const expected = {
    _type: "formGroup",
    fieldName: "key",
    fieldKey: "key",
    isRequired: false,
    properties: [
      {
        _type: "formItem",
        description: "Hostname of the database.",
        fieldName: "key.host",
        fieldKey: "host",
        isRequired: true,
        type: "string",
      },
      {
        _type: "formItem",
        description: "Port of the database.",
        fieldName: "key.port",
        fieldKey: "port",
        isRequired: true,
        type: "integer",
      },
      {
        _type: "formItem",
        description: "Username to use to access the database.",
        fieldName: "key.user",
        fieldKey: "user",
        isRequired: true,
        type: "string",
      },
      {
        _type: "formItem",
        description: "Name of the database.",
        fieldName: "key.dbname",
        fieldKey: "dbname",
        isRequired: true,
        type: "string",
      },
      {
        _type: "formItem",
        description: "Password associated with the username.",
        fieldName: "key.password",
        fieldKey: "password",
        isRequired: false,
        isSecret: true,
        type: "string",
      },
    ],
  };

  expect(builtSchema).toEqual(expected);
});

test("should reformat jsonSchema to internal widget representation with parent schema", () => {
  const schema: JSONSchema7 = {
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
    title: "Postgres Source Spec",
    _type: "formGroup",
    fieldName: "key",
    fieldKey: "key",
    isRequired: true,
    properties: [
      {
        _type: "formItem",
        description: "Hostname of the database.",
        fieldName: "key.host",
        fieldKey: "host",
        isRequired: true,
        type: "string",
      },
    ],
  };

  expect(builtSchema).toEqual(expected);
});

test("should reformat jsonSchema to internal widget representation when has oneOf", () => {
  const schema: JSONSchema7 = {
    type: "object",
    required: ["start_date", "credentials"],
    properties: {
      start_date: {
        type: "string",
      },
      credentials: {
        type: "object",
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
    fieldKey: "key",
    fieldName: "key",
    isRequired: true,
    properties: [
      {
        _type: "formItem",
        fieldKey: "start_date",
        fieldName: "key.start_date",
        isRequired: true,
        type: "string",
      },
      {
        _type: "formCondition",
        conditions: {
          "api key": {
            title: "api key",
            _type: "formGroup",
            fieldKey: "credentials",
            fieldName: "key.credentials",
            isRequired: false,
            properties: [
              {
                _type: "formItem",
                fieldKey: "api_key",
                fieldName: "key.credentials.api_key",
                isRequired: true,
                type: "string",
              },
            ],
          },
          oauth: {
            title: "oauth",
            _type: "formGroup",
            fieldKey: "credentials",
            fieldName: "key.credentials",
            isRequired: false,
            properties: [
              {
                _type: "formItem",
                examples: ["https://api.hubspot.com/"],
                fieldKey: "redirect_uri",
                fieldName: "key.credentials.redirect_uri",
                isRequired: true,
                type: "string",
              },
            ],
          },
        },
        fieldKey: "credentials",
        fieldName: "key.credentials",
        isRequired: true,
      },
    ],
  };

  expect(builtSchema).toEqual(expected);
});
