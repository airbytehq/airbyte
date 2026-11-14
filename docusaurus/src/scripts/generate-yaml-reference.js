const fs = require("fs");
const path = require("path");
const yaml = require("js-yaml");

const schema = yaml.load(
  fs.readFileSync(
    path.join(__dirname, "../data/declarative_component_schema.yaml"),
    "utf8",
  ),
);
const output = path.resolve(
  __dirname,
  "../../../docs/platform/connector-development/config-based/understanding-the-yaml-file/reference",
);
const components = { [schema.title]: schema, ...schema.definitions };
const names = [schema.title, ...Object.keys(schema.definitions).sort()];
const files = new Map();
const interpolation = structuredClone(schema.interpolation);
const variableNames = new Set(
  interpolation.variables.map((item) => item.title),
);
function collectContextVariables(node) {
  if (!node || typeof node !== "object") return;
  for (const title of node.interpolation_context || []) {
    if (!variableNames.has(title)) {
      interpolation.variables.push({ title });
      variableNames.add(title);
    }
  }
  Object.values(node).forEach(collectContextVariables);
}
collectContextVariables(schema);
const code = (value) =>
  `\`${typeof value === "string" ? value : JSON.stringify(value)}\``;
const escapeAttribute = (value) =>
  value
    .replaceAll("&", "&amp;")
    .replaceAll('"', "&quot;")
    .replaceAll("<", "&lt;");
const heading = (name, id = name) => `## ${name} {#${id}}\n\n`;
const frontMatter = (title, extra = "") =>
  `---\nformat: md\nmdx:\n  format: md\ntitle: ${JSON.stringify(title)}\n${extra}---\n\n# ${title}\n\n`;

function examples(values) {
  if (!values?.length) return "";
  return (
    "Examples:\n\n" +
    values
      .map((value) => {
        const content =
          typeof value === "string"
            ? value
            : yaml.dump(value, { lineWidth: -1, noRefs: true });
        const fence = "`".repeat(
          Math.max(
            3,
            ...[...content.matchAll(/`+/g)].map((match) => match[0].length + 1),
          ),
        );
        return `${fence}yaml\n${content.trimEnd()}\n${fence}\n\n`;
      })
      .join("")
  );
}

function reference(ref) {
  const name = ref.replace(/^#\/definitions\//, "");
  if (Object.hasOwn(components, name)) return `[${code(name)}](./${name}.md)`;
  console.warn(`Unknown YAML reference: ${ref}`);
  return code(ref);
}

function details(node, required) {
  let text = node.description ? `${node.description}\n\n` : "";
  if (required !== undefined)
    text += `- Required: ${required ? "Yes" : "No"}\n`;
  for (const key of [
    "type",
    "default",
    "enum",
    "const",
    "minimum",
    "exclusiveMinimum",
    "maximum",
    "exclusiveMaximum",
    "multipleOf",
    "minLength",
    "maxLength",
    "pattern",
    "format",
    "minItems",
    "maxItems",
    "uniqueItems",
    "minProperties",
    "maxProperties",
    "required",
  ]) {
    if (Object.hasOwn(node, key)) text += `- ${key}: ${code(node[key])}\n`;
  }
  if (node.deprecated || node.deprecation_message)
    text += `- Deprecated: ${code(node.deprecated ?? true)}${node.deprecation_message ? ` — ${node.deprecation_message}` : ""}\n`;
  if (node.$ref) text += `- Allowed type: ${reference(node.$ref)}\n`;
  if (node.interpolation_context)
    text += `- Available variables: ${node.interpolation_context.map((name) => `[${code(name)}](./variables.md#${name})`).join(", ")}\n`;
  return text + "\n" + examples(node.examples);
}

function children(node, prefix, renderProperty) {
  let text = "";
  for (const [name, property] of Object.entries(node.properties || {})) {
    text += renderProperty(
      name,
      property,
      prefix ? `${prefix}.${name}` : name,
      (node.required || []).includes(name),
    );
  }
  for (const key of [
    "anyOf",
    "oneOf",
    "allOf",
    "items",
    "additionalProperties",
  ]) {
    if (!node[key] || typeof node[key] !== "object") continue;
    const variants = Array.isArray(node[key]) ? node[key] : [node[key]];
    variants.forEach((variant) => {
      text +=
        `- ${key}:\n\n` +
        (details(variant) + children(variant, prefix, renderProperty))
          .split("\n")
          .map((line) => (line ? `  ${line}` : ""))
          .join("\n") +
        "\n";
    });
  }
  return text;
}

for (const name of names) {
  const node = components[name];
  const anchors = new Set();
  const property = (label, value, dotted, required) => {
    const anchor = anchors.has(dotted)
      ? ""
      : `<a id="${escapeAttribute(dotted)}"></a> `;
    anchors.add(dotted);
    const body = details(value, required) + children(value, dotted, property);
    return (
      `- ${anchor}**${code(label)}**\n\n` +
      body
        .split("\n")
        .map((line) => (line ? `  ${line}` : ""))
        .join("\n") +
      "\n"
    );
  };
  let text = frontMatter(name) + details(node);
  for (const [label, value] of Object.entries(node.properties || {})) {
    anchors.add(label);
    text +=
      heading(label) +
      details(value, (node.required || []).includes(label)) +
      children(value, label, property);
  }
  const withoutProperties = { ...node, properties: undefined };
  text += children(withoutProperties, "", property);
  files.set(`${name}.md`, text);
}

const intros = {
  variables:
    "All string properties that list out available variables allow [jinja expressions](https://jinja.palletsprojects.com/en/3.0.x/templates/#expressions). They can be used by placing them in double curly braces: `{{ config.property }}`. The following variables are available.",
  macros:
    "Besides referencing variables, the following macros can be called as part of [jinja expressions](https://jinja.palletsprojects.com/en/3.0.x/templates/#expressions), for example like this: `{{ now_utc() }}`.",
  filters:
    "The following filters can be called as part of [jinja expressions](https://jinja.palletsprojects.com/en/3.0.x/templates/#expressions), for example like this: `{{  1 | string  }}`.",
};
for (const [group, intro] of Object.entries(intros)) {
  let text = frontMatter(`Interpolation ${group}`) + intro + "\n\n";
  for (const item of interpolation[group]) {
    text += heading(item.title) + details(item);
    if (Object.keys(item.arguments || {}).length)
      text +=
        "Arguments:\n\n" +
        Object.entries(item.arguments)
          .map(
            ([name, value]) =>
              `- ${code(name)}: ${typeof value === "string" ? value : code(value)}\n`,
          )
          .join("") +
        "\n";
  }
  files.set(`${group}.md`, text);
}
let index =
  frontMatter(
    "YAML reference",
    "slug: /connector-development/config-based/understanding-the-yaml-file/reference\nsidebar_position: 0\n",
  ) +
  "This reference lists the components and interpolation helpers available when defining a low code YAML file.\n\nSee the [raw schema on GitHub](https://github.com/airbytehq/airbyte-python-cdk/blob/main/airbyte_cdk/sources/declarative/declarative_component_schema.yaml) for the technical schema used to validate manifests.\n\n";
index +=
  "[Variables](./variables.md) · [Macros](./macros.md) · [Filters](./filters.md)\n\n| Component | Description |\n| --- | --- |\n";
for (const name of names) {
  const description = (components[name].description || "").match(
    /^[\s\S]*?(?:\.(?=\s|$)|$)/,
  )[0];
  index += `| [${name}](./${name}.md) | ${description.replaceAll("\n", " ").replaceAll("|", "\\|")} |\n`;
}
files.set("index.md", index);

if (!process.argv.includes("--check")) {
  fs.writeFileSync(
    path.join(__dirname, "../data/yaml-reference-links.json"),
    JSON.stringify({
      definitions: names,
      ...Object.fromEntries(
        Object.keys(intros).map((group) => [
          group,
          interpolation[group].map((item) => item.title),
        ]),
      ),
    }),
  );
  fs.mkdirSync(output, { recursive: true });
  for (const file of fs.readdirSync(output))
    if (file.endsWith(".md") && !files.has(file))
      fs.unlinkSync(path.join(output, file));
  for (const [file, content] of files)
    fs.writeFileSync(path.join(output, file), content);
}
let propertyCount = 0;
function checkPaths(node, prefix, paths) {
  for (const [name, value] of Object.entries(node.properties || {})) {
    const dotted = prefix ? `${prefix}.${name}` : name;
    paths.add(dotted);
    checkPaths(value, dotted, paths);
  }
  for (const key of [
    "anyOf",
    "oneOf",
    "allOf",
    "items",
    "additionalProperties",
  ]) {
    const value = node[key];
    if (value && typeof value === "object")
      (Array.isArray(value) ? value : [value]).forEach((entry) =>
        checkPaths(entry, prefix, paths),
      );
  }
}
for (const name of names) {
  const content = fs.readFileSync(path.join(output, `${name}.md`), "utf8");
  if (!content.includes(`# ${name}\n`))
    throw new Error(`Missing component: ${name}`);
  const paths = new Set();
  checkPaths(components[name], "", paths);
  for (const dotted of paths) {
    if (
      !content.includes(`{#${dotted}}`) &&
      !content.includes(`id="${escapeAttribute(dotted)}"`)
    )
      throw new Error(`Missing property: ${name}.${dotted}`);
  }
  propertyCount += paths.size;
}
console.log(
  `YAML reference coverage: ${Object.keys(schema.definitions).length} definitions + 1 root; ${propertyCount} property paths; ${files.size} pages`,
);
