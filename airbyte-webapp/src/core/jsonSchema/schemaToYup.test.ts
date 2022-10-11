import * as yup from "yup";

import { buildYupFormForJsonSchema } from "./schemaToYup";
import { AirbyteJSONSchema } from "./types";

// Note: We have to check yup schema with JSON.stringify
// as exactly same objects throw now equality due to `Received: serializes to the same string` error
it("should build schema for simple case", () => {
  const schema: AirbyteJSONSchema = {
    type: "object",
    title: "Postgres Source Spec",
    required: ["host", "port", "user", "dbname", "is_field_no_default"],
    properties: {
      host: { type: "string", description: "Hostname of the database." },
      port: {
        type: "integer",
        maximum: 65536,
        minimum: 0,
        description: "Port of the database.",
      },
      user: {
        type: "string",
        description: "Username to use to access the database.",
      },
      is_sandbox: {
        type: "boolean",
        default: false,
      },
      is_field_no_default: {
        type: "boolean",
      },
      dbname: { type: "string", description: "Name of the database." },
      password: {
        type: "string",
        description: "Password associated with the username.",
      },
      reports: {
        type: "array",
        items: {
          type: "string",
        },
      },
    },
    additionalProperties: false,
  };
  const yupSchema = buildYupFormForJsonSchema(schema);

  const expectedSchema = yup.object().shape({
    host: yup.string().trim().required("form.empty.error"),
    port: yup.number().min(0).max(65536).required("form.empty.error"),
    user: yup.string().trim().required("form.empty.error"),
    is_sandbox: yup.boolean().default(false),
    is_field_no_default: yup.boolean().required("form.empty.error"),
    dbname: yup.string().trim().required("form.empty.error"),
    password: yup.string().trim(),
    reports: yup.array().of(yup.string().trim()),
  });

  expect(JSON.stringify(yupSchema)).toEqual(JSON.stringify(expectedSchema));
});

it("should build schema for conditional case", () => {
  const yupSchema = buildYupFormForJsonSchema(
    {
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
    },
    { credentials: { selectedItem: "api key" } }
  );

  const expectedSchema = yup.object().shape({
    start_date: yup.string().trim().required("form.empty.error"),
    credentials: yup.object().shape({
      api_key: yup.string().trim().required("form.empty.error"),
    }),
  });

  expect(JSON.stringify(yupSchema)).toEqual(JSON.stringify(expectedSchema));
});

it("should build schema for conditional case with inner schema and selected uiwidget", () => {
  const yupSchema = buildYupFormForJsonSchema(
    {
      type: "object",
      properties: {
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
    },
    { "topKey.subKey.credentials": { selectedItem: "oauth" } },
    undefined,
    "topKey",
    "topKey.subKey"
  );

  const expectedSchema = yup.object().shape({
    credentials: yup.object().shape({
      redirect_uri: yup.string().trim().required("form.empty.error"),
    }),
  });

  expect(JSON.stringify(yupSchema)).toEqual(JSON.stringify(expectedSchema));
});
