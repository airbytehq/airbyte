import { JSONSchema6 } from "json-schema";
import * as yup from "yup";
import { buildYupFormForJsonSchema } from "./yupHelper";

test("should build schema for simple case", () => {
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
  const yupSchema = buildYupFormForJsonSchema(schema);

  expect(yupSchema).toEqual(
    yup.object().shape({
      host: yup.string().required("form.empty.error"),
      port: yup
        .number()
        .min(0)
        .max(65536)
        .required("form.empty.error"),
      user: yup.string().required("form.empty.error"),
      dbname: yup.string().required("form.empty.error"),
      password: yup.string()
    })
  );
});

test("should build schema for conditional case", () => {
  const yupSchema = buildYupFormForJsonSchema(
    {
      type: "object",
      required: ["start_date", "credentials"],
      properties: {
        start_date: {
          type: "string"
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
              required: ["redirect_uri"],
              properties: {
                redirect_uri: {
                  type: "string",
                  examples: ["https://api.hubspot.com/"]
                }
              }
            }
          ]
        }
      }
    },
    { credentials: { selectedItem: "api key" } }
  );

  const expected = yup.object().shape({
    start_date: yup.string().required("form.empty.error"),
    credentials: yup.object().shape({
      api_key: yup.string().required("form.empty.error")
    })
  });

  expect(JSON.stringify(yupSchema)).toEqual(JSON.stringify(expected));
});
