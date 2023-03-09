import * as yup from "yup";

import { AirbyteJSONSchema } from "core/jsonSchema/types";

import { jsonSchemaToFormBlock } from "./schemaToFormBlock";
import { buildYupFormForJsonSchema } from "./schemaToYup";

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
  const yupSchema = buildYupFormForJsonSchema(schema, jsonSchemaToFormBlock(schema));

  const expectedSchema = yup.object().shape({
    host: yup.string().trim().required("form.empty.error").transform(String),
    port: yup
      .number()
      .min(0)
      .max(65536)
      .required("form.empty.error")
      .transform((val) => (isNaN(val) ? undefined : val)),
    user: yup.string().trim().required("form.empty.error").transform(String),
    is_sandbox: yup.boolean().default(false),
    is_field_no_default: yup.boolean().required("form.empty.error"),
    dbname: yup.string().trim().required("form.empty.error").transform(String),
    password: yup.string().trim().transform(String),
    reports: yup.array().of(yup.string().trim().transform(String)),
  });

  expect(JSON.stringify(yupSchema)).toEqual(JSON.stringify(expectedSchema));
});

const simpleConditionalSchema: AirbyteJSONSchema = {
  type: "object",
  required: ["start_date", "credentials"],
  properties: {
    start_date: {
      type: "string",
    },
    max_objects: {
      type: "number",
    },
    credentials: {
      type: "object",
      oneOf: [
        {
          title: "api key",
          required: ["type", "api_key"],
          properties: {
            api_key: {
              type: "string",
              pattern: "\\w{5}",
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
          required: ["type", "redirect_uri"],
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

it("should build correct mixed schema structure for conditional case", () => {
  const yupSchema = buildYupFormForJsonSchema(simpleConditionalSchema, jsonSchemaToFormBlock(simpleConditionalSchema));

  const expectedSchema = yup.object().shape({
    start_date: yup.string().trim().required("form.empty.error").transform(String),
    max_objects: yup.number().transform((x) => x),
    credentials: yup.object().shape({
      type: yup.mixed(),
      api_key: yup
        .mixed()
        // Using dummy callbacks for then and otherwise as this test only checks whether the yup schema is structured as expected, it's not asserting that it validates form values as expected.
        .when("type", { is: "", then: (x) => x, otherwise: (x) => x })
        .when("type", { is: "", then: (x) => x, otherwise: (x) => x }),
      redirect_uri: yup
        .mixed()
        .when("type", { is: "", then: (x) => x, otherwise: (x) => x })
        .when("type", { is: "", then: (x) => x, otherwise: (x) => x }),
    }),
  });

  expect(JSON.parse(JSON.stringify(yupSchema))).toEqual(JSON.parse(JSON.stringify(expectedSchema)));
});

// These tests check whether the built yup schema validates as expected, it is not checking the structure
describe("yup schema validations", () => {
  const yupSchema = buildYupFormForJsonSchema(simpleConditionalSchema, jsonSchemaToFormBlock(simpleConditionalSchema));
  it("enforces required props for selected condition", () => {
    expect(() => {
      yupSchema.validateSync({
        start_date: "2022",
        max_objects: 5,
        credentials: {
          // api needs api_key, so this should fail
          type: "api",
          redirect_uri: "test",
        },
      });
    }).toThrowError("form.empty.error");
  });

  it("does not enforce additional contraints if the condition is selected", () => {
    expect(() => {
      yupSchema.validateSync({
        start_date: "2022",
        max_objects: 5,
        credentials: {
          type: "oauth",
          redirect_uri: "test",
          // does not match the pattern, but it should not be validated
          api_key: "X",
        },
      });
    }).not.toThrowError();
  });

  it("enforces additional contraints only if the condition is selected", () => {
    expect(() => {
      yupSchema.validateSync({
        start_date: "2022",
        max_objects: 5,
        credentials: {
          type: "api",
          // does not match the pattern, so it should fail
          api_key: "X",
        },
      });
    }).toThrowError("form.pattern.error");
  });

  it("strips out properties belonging to other conditions", () => {
    const cleanedValues = yupSchema.cast(
      {
        start_date: "2022",
        max_objects: 5,
        credentials: {
          type: "api",
          api_key: "X",
          redirect_uri: "test",
        },
      },
      {
        stripUnknown: true,
      }
    );
    expect(cleanedValues.credentials).toEqual({
      type: "api",
      api_key: "X",
    });
  });

  it("does not strip out any properties if the condition key is not set to prevent data loss of legacy specs", () => {
    const cleanedValues = yupSchema.cast(
      {
        start_date: "2022",
        max_objects: 5,
        credentials: {
          api_key: "X",
          redirect_uri: "test",
        },
      },
      {
        stripUnknown: true,
      }
    );
    expect(cleanedValues.credentials).toEqual({
      api_key: "X",
      redirect_uri: "test",
    });
  });
});
