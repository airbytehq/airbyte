const fs = require("fs");
const Handlebars = require("Handlebars");
const YAML = require('yaml');
const _ = require("lodash");

const manifestSchemaYaml = fs.readFileSync('../python/airbyte_cdk/sources/declarative/declarative_component_schema.yaml', 'utf8')
const manifestSchema = YAML.parse(manifestSchemaYaml);

function descriptionWithSchema(path) {
    const schemaPart = _.get(manifestSchema, path);
    if (!schemaPart) {
        throw new Error("Did not find " + path);
    }
    const title = schemaPart.title || path.split(".").at(-1);
    if (schemaPart.title) {
        delete schemaPart.title;
    }
    const description = schemaPart.description;
    if (description) {
        delete schemaPart.description;
    }

    const examples = schemaPart.examples;
    if (examples) {
        delete schemaPart.examples;
    }

    return new Handlebars.SafeString(`### ${title}${description ? `

${description}
` : ""}
Schema: 

\`\`\`yaml
${YAML.stringify(schemaPart)}
\`\`\`${examples ? `\n\nExample${examples.length > 1 ? "s" : ""}:\n\n` + examples.join("\n\n") : ""}`);
}

function descriptionWithSchemaForEachRef(path) {
    const schemaPart = _.get(manifestSchema, path);
    if (!schemaPart) {
        throw new Error("Did not find " + path);
    }
    return new Handlebars.SafeString(schemaPart.map(refObj => /definitions\/(.*)/.exec(refObj["$ref"])[1]).map(def => `definitions.${def}`).map(descriptionWithSchema).join("\n\n"));
}

function loadTemplate(file) {
    const contents = fs.readFileSync("./pages/"+file, { encoding: "utf8"});
    return `
<!---
    Auto-generated file, do not edit here.
    Template is located in "airbyte-cdk/low_code_docs_generation/pages/${file}"
-->
${contents}`;
}

Handlebars.registerHelper('descriptionWithSchema', descriptionWithSchema);
Handlebars.registerHelper('descriptionWithSchemaForEachRef', descriptionWithSchemaForEachRef);


const pageFiles = fs.readdirSync("./pages");
pageFiles.forEach(file => {
    if (!file.endsWith(".md.hbs")) return;
    console.log("Compiling " + file);
    const template = Handlebars.compile(loadTemplate(file));
    const result = template();
    const target = "../../docs/connector-development/config-based/understanding-the-yaml-file/" + file.slice(0, -4);
    console.log("Writing " + target);
    fs.writeFileSync(target, result)
});