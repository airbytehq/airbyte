import { AirbyteJSONSchema } from "./types";
import { removeNestedPaths } from "./utils";

test("should filter paths", () => {
  const schema: AirbyteJSONSchema = {
    type: "object",
    properties: {
      host: { type: "string" },
      port: { type: "string" },
      name: { type: "string" },
      db: {
        type: "object",
        properties: {
          url: { type: "string" },
        },
      },
      ssl: {
        type: "object",
        properties: {
          ssl_done: { type: "string" },
          ssl_string: { type: "string" },
        },
      },
    },
  };

  const filtered = removeNestedPaths(schema, [["host"], ["ssl"]]);

  expect(filtered).toEqual({
    properties: {
      db: {
        properties: {
          url: {
            type: "string",
          },
        },
        type: "object",
      },
      name: {
        type: "string",
      },
      port: {
        type: "string",
      },
    },
    type: "object",
  });
});

test("should exclude nested paths", () => {
  const schema: AirbyteJSONSchema = {
    type: "object",
    properties: {
      ssl: {
        type: "object",
        properties: {
          ssl_done: { type: "string" },
          ssl_port: { type: "string" },
          ssl_object: {
            type: "object",
            properties: {
              ssl_object_ref: {
                type: "string",
              },
              ssl_object_ref2: {
                type: "string",
              },
            },
          },
        },
      },
    },
  };

  const filtered = removeNestedPaths(schema, [
    ["ssl", "ssl_object", "ssl_object_ref2"],
    ["ssl", "ssl_done"],
  ]);

  expect(filtered).toEqual({
    properties: {
      ssl: {
        properties: {
          ssl_port: {
            type: "string",
          },
          ssl_object: {
            properties: {
              ssl_object_ref: {
                type: "string",
              },
            },
            type: "object",
          },
        },
        type: "object",
      },
    },
    type: "object",
  });
});
