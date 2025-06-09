import ManifestYamlDefinitions from '@site/src/components/ManifestYamlDefinitions';
import schema from "@site/src/data/declarative_component_schema.yaml";

# YAML Reference

This page lists all components, interpolation variables and interpolation macros that can be used when defining a low code YAML file.

For the technical JSON schema definition that low code manifests are validated against, see [here](https://github.com/airbytehq/airbyte-python-cdk/blob/main/airbyte_cdk/sources/declarative/declarative_component_schema.yaml).

<ManifestYamlDefinitions />

export const toc = [
{
"value": "Components:",
"id": "components",
"level": 2
},
{
value: "DeclarativeSource",
id: "/definitions/DeclarativeSource",
level: 3
},
...Object.keys(schema.definitions).map((id) => ({
value: id,
id: `/definitions/${id}`,
level: 3
})),
{
"value": "Interpolation variables:",
"id": "variables",
"level": 2
},
...schema.interpolation.variables.map((def) => ({
value: def.title,
id: `/variables/${def.title}`,
level: 3
})),
{
"value": "Interpolation macros:",
"id": "macros",
"level": 2
},
...schema.interpolation.macros.map((def) => ({
value: def.title,
id: `/macros/${def.title}`,
level: 3
})),
{
"value": "Interpolation filters:",
"id": "filters",
"level": 2
},
...schema.interpolation.filters.map((def) => ({
value: def.title,
id: `/filters/${def.title}`,
level: 3
}))
];
