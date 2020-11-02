import { jsonSchemaToUiWidget } from "./uiWidget";
import { JSONSchema6 } from "json-schema";

test("should reformat jsonSchema to internal widget representation", () => {
  const schema: JSONSchema6 = {
    type: "object",
    title: "Postgres Source Spec",
    required: ["host", "port", "user", "dbname"],
    properties: {
      host: { type: "string", description: "Hostname of the database." },
      port: {
        type: "integer",
        maximum: 65536,
        minimum: 0,
        description: "Port of the database."
      },
      user: {
        type: "string",
        description: "Username to use to access the database."
      },
      dbname: { type: "string", description: "Name of the database." },
      password: {
        type: "string",
        description: "Password associated with the username."
      }
    },
    additionalProperties: false
  };

  const builtSchema = jsonSchemaToUiWidget(schema, "key");

  const expected = {
    _type: "group",
    fieldName: "key",
    isRequired: false,
    properties: [
      {
        _type: "form-fieldKey",
        description: "Hostname of the database.",
        fieldName: "key.host",
        isRequired: true,
        type: "string"
      },
      {
        _type: "form-fieldKey",
        description: "Port of the database.",
        fieldName: "key.port",
        isRequired: true,
        type: "integer"
      },
      {
        _type: "form-fieldKey",
        description: "Username to use to access the database.",
        fieldName: "key.user",
        isRequired: true,
        type: "string"
      },
      {
        _type: "form-fieldKey",
        description: "Name of the database.",
        fieldName: "key.dbname",
        isRequired: true,
        type: "string"
      },
      {
        _type: "form-fieldKey",
        description: "Password associated with the username.",
        fieldName: "key.password",
        isRequired: false,
        type: "string"
      }
    ]
  };

  expect(builtSchema).toEqual(expected);
});

test("should reformat jsonSchema to internal widget representation with parent schema", () => {
  const schema: JSONSchema6 = {
    type: "object",
    title: "Postgres Source Spec",
    required: ["host", "port", "user", "dbname"],
    properties: {
      host: { type: "string", description: "Hostname of the database." }
    },
    additionalProperties: false
  };

  const builtSchema = jsonSchemaToUiWidget(schema, "key", undefined, {
    required: ["key"]
  });

  const expected = {
    _type: "group",
    fieldName: "key",
    isRequired: true,
    properties: [
      {
        _type: "form-fieldKey",
        description: "Hostname of the database.",
        fieldName: "key.host",
        isRequired: true,
        type: "string"
      }
    ]
  };

  expect(builtSchema).toEqual(expected);
});

test("should reformat jsonSchema to internal widget representation when has oneOf", () => {
  const schema: JSONSchema6 = {
    type: "object",
    required: ["start_date", "credentials"],
    properties: {
      start_date: {
        type: "string",
        pattern: "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$",
        description:
          "UTC date and time in the format 2017-01-25T00:00:00Z. Any data before this date will not be replicated.",
        examples: ["2017-01-25T00:00:00Z"]
      },
      credentials: {
        type: "object",
        oneOf: [
          {
            title: "api key",
            required: ["api_key"],
            properties: {
              api_key: {
                type: "string"
              }
            }
          },
          {
            title: "oauth",
            required: [
              "redirect_uri",
              "client_id",
              "client_secret",
              "refresh_token"
            ],
            properties: {
              redirect_uri: {
                type: "string",
                examples: ["https://api.hubspot.com/"]
              },
              client_id: {
                type: "string",
                examples: ["123456789000,"]
              },
              client_secret: {
                type: "string",
                examples: ["secret"]
              },
              refresh_token: {
                type: "string",
                examples: ["refresh_token"]
              }
            }
          }
        ]
      }
    }
  };

  const builtSchema = jsonSchemaToUiWidget(schema, "key", undefined, {
    required: ["key"]
  });

  const expected = {
    _type: "group",
    fieldName: "key",
    isRequired: true,
    properties: [
      {
        _type: "form-fieldKey",
        description: "Hostname of the database.",
        fieldName: "key.host",
        isRequired: true,
        type: "string"
      }
    ]
  };

  expect(builtSchema).toEqual(expected);
});
