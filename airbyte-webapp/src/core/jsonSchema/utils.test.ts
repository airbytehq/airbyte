import { AirbyteJSONSchema } from "./types";
import { applyFuncAt, removeNestedPaths } from "./utils";

test("should filter paths", () => {
  const schema: AirbyteJSONSchema = {
    type: "object",
    required: ["host", "name"],
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
    required: ["name"],
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

test("should exclude paths in oneOf", () => {
  const schema: AirbyteJSONSchema = {
    type: "object",
    properties: {
      ssl: {
        type: "object",
        oneOf: [
          {
            properties: {
              ssl_string: {
                type: "string",
              },
            },
          },
          {
            properties: {
              ssl_path: {
                type: "string",
              },
            },
          },
        ],
      },
    },
  };

  const filtered = removeNestedPaths(schema, [["ssl", "ssl_string"]]);

  expect(filtered).toEqual({
    properties: {
      ssl: {
        oneOf: [
          {
            properties: {},
          },
          {
            properties: {
              ssl_path: {
                type: "string",
              },
            },
          },
        ],
        type: "object",
      },
    },
    type: "object",
  });
});

test("apply func at", () => {
  const schema: AirbyteJSONSchema = {
    type: "object",
    properties: {
      ssl: {
        type: "object",
        oneOf: [
          {
            properties: {
              ssl_string: {
                type: "string",
              },
            },
          },
          {
            properties: {
              ssl_path: {
                type: "string",
              },
            },
          },
        ],
      },
    },
  };

  const applied = applyFuncAt(schema, ["ssl", 0], (sch) => {
    if (typeof sch === "boolean") {
      return sch as any;
    }

    sch.properties = sch.properties ?? {};

    sch.properties["marked"] = {
      type: "string",
    };

    return sch;
  });

  expect(applied).toEqual({
    type: "object",
    properties: {
      ssl: {
        type: "object",
        oneOf: [
          {
            properties: {
              ssl_string: {
                type: "string",
              },
              marked: {
                type: "string",
              },
            },
          },
          {
            properties: {
              ssl_path: {
                type: "string",
              },
            },
          },
        ],
      },
    },
  });
});
