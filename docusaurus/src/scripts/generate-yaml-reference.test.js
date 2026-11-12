const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");
const yaml = require("js-yaml");

const source = fs.readFileSync(
  path.join(__dirname, "generate-yaml-reference.js"),
  "utf8",
);
function generate(overrides = {}, check = false, files = new Map()) {
  const fixture = {
    title: "Root",
    definitions: {},
    interpolation: { variables: [], macros: [], filters: [] },
    ...overrides,
  };
  const warnings = [];
  vm.runInNewContext(source, {
    __dirname,
    require: (name) =>
      name === "fs"
        ? {
            readFileSync: (file) =>
              file.endsWith(".yaml")
                ? yaml.dump(fixture)
                : files.get(path.basename(file)),
            writeFileSync: (file, content) =>
              files.set(path.basename(file), content),
            mkdirSync: () => {},
            readdirSync: () => [...files.keys()],
            unlinkSync: (file) => files.delete(path.basename(file)),
          }
        : require(name),
    process: { argv: check ? ["--check"] : [] },
    structuredClone,
    console: { log: () => {}, warn: (message) => warnings.push(message) },
  });
  return { files, warnings };
}

test("empty schema produces root, index and interpolation pages; stale files are removed", () => {
  const { files } = generate({}, false, new Map([["stale.md", "old"]]));
  assert.equal(
    [...files.keys()].filter((file) => file.endsWith(".md")).length,
    5,
  );
  assert.ok(files.get("Root.md").includes("format: md"));
  assert.ok(!files.has("stale.md"));
});

test("recursive variants, items and additionalProperties preserve paths and metadata", () => {
  const fixture = {
    definitions: {
      Component: {
        type: "object",
        required: ["outer"],
        properties: {
          outer: {
            anyOf: [
              {
                type: "object",
                properties: {
                  nested: {
                    type: "array",
                    items: {
                      additionalProperties: {
                        properties: {
                          leaf: {
                            type: "integer",
                            minimum: 0,
                            default: 0,
                            deprecated: true,
                            deprecation_message: "Use replacement.",
                            examples: [{ value: 1 }],
                          },
                        },
                      },
                    },
                  },
                },
              },
              { $ref: "#/definitions/Component" },
            ],
          },
        },
      },
    },
  };
  const { files } = generate(fixture);
  const page = files.get("Component.md");
  for (const value of [
    "Required: Yes",
    'id="outer.nested.leaf"',
    "minimum: `0`",
    "default: `0`",
    "Deprecated: `true` — Use replacement.",
    "```yaml",
    "value: 1",
    "./Component.md",
  ])
    assert.ok(page.includes(value), value);
  assert.ok(!/^####/m.test(page));
  generate(fixture, true, files);
  files.set("Component.md", page.replace('id="outer.nested.leaf"', ""));
  assert.throws(
    () => generate(fixture, true, files),
    /Missing property: Component.outer.nested.leaf/,
  );
});

test("missing references warn, context-only variables get anchors, and string examples stay intact", () => {
  const { files, warnings } = generate({
    properties: {
      value: {
        $ref: "#/definitions/Missing",
        interpolation_context: ["context_only"],
        examples: ["{{ config.value }} < 5"],
      },
    },
  });
  assert.deepEqual(warnings, ["Unknown YAML reference: #/definitions/Missing"]);
  assert.ok(
    files.get("Root.md").includes("```yaml\n{{ config.value }} < 5\n```"),
  );
  assert.ok(!files.get("Root.md").includes("./Missing.md"));
  assert.ok(
    files.get("variables.md").includes("## context_only {#context_only}"),
  );
});

test("legacy hashes redirect only known names on the reference index", () => {
  const redirectSource = fs
    .readFileSync(path.join(__dirname, "yaml-reference-redirect.js"), "utf8")
    .replace(/^import .*;\n/, "")
    .replaceAll("export function", "function");
  const context = {
    links: {
      definitions: ["Root", "Component"],
      variables: ["config"],
      macros: [],
      filters: [],
    },
  };
  vm.createContext(context);
  vm.runInContext(redirectSource, context);
  const base =
    "/platform/connector-development/config-based/understanding-the-yaml-file/reference";
  for (const [pathname, hash, expected] of [
    [base, "#/definitions/Root", `${base}/Root`],
    [base + "/", "#/definitions/Component", `${base}/Component`],
    [base, "#/variables/config", `${base}/variables#config`],
    [base, "#/definitions/Unknown", undefined],
    [base, "#/macros/Unknown", undefined],
    [base, "#components", undefined],
    [base + "/Component", "#/variables/config", undefined],
  ]) {
    let destination;
    context.redirectLegacyHash({
      pathname,
      hash,
      replace: (value) => (destination = value),
    });
    assert.equal(destination, expected);
  }
});
