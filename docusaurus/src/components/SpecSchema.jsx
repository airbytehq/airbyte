import React from "react";
import styles from "./SpecSchema.module.css";
import sanitizeHtml from "sanitize-html";

export const SpecSchema = ({
  specJSON
}) => {
  const spec = JSON.parse(specJSON);
  spec.description = undefined;
  spec.title = "Config fields";
  return <>
    <JSONSchemaViewer schema={spec} />
  </>;
};

function JSONSchemaViewer(props) {
  return <div>
    <pre>{JSON.stringify(props.schema, null, 2)}</pre>
    <JSONSchemaObject schema={props.schema} />
  </div>
}

function JSONSchemaObject(props) {
  const requiredProperties = new Set(props.schema.required || []);
  return <div>
    {Object.entries(props.schema.properties).map(([key, schema]) => {
      return <JSONSchemaProperty key={key} propertyKey={key} schema={schema} required={requiredProperties.has(key)} />
    })}
  </div>
}

function JSONSchemaOneOf(props) {
  return <div>
    oneOf:
    <ul>
      {props.schema.oneOf.map((schema, i) => {
        return <li key={i}>
          <JSONSchemaProperty schema={schema} />
        </li>
      })}
    </ul>
  </div>
}

const allowedAttributes = {
  ...sanitizeHtml.defaults.allowedAttributes,
  a: [...sanitizeHtml.defaults.allowedAttributes.a, "rel"],
};

const TextWithHTML = ({ text, className }) => {
  if (!text) {
    return null;
  }

  const sanitizedHtmlText = sanitizeHtml(text, {
    allowedAttributes,
    transformTags: {
      a: sanitizeHtml.simpleTransform("a", {
        target: "_blank",
        rel: "noopener noreferrer",
      }),
    },
  });

  return <span className={className} dangerouslySetInnerHTML={{ __html: sanitizedHtmlText }} />;
};

function JSONSchemaProperty({ propertyKey, schema, required }) {
  return <div className={styles.block}>
    <div>
      <div className={styles.header}>
        {propertyKey && <div>{propertyKey}</div>}
        {schema.title && <div>{schema.title}</div>}
        {required && <div>REQUIRED!</div>}
        {schema.const && <div>constant value: <pre>{schema.default}</pre></div>}
      </div>
      <div>type: {schema.type}</div>
      {schema.default && !schema.const && <div>default: <pre>{JSON.stringify(schema.default, null, 2)}</pre></div>}
      {schema.pattern && <div>pattern: {schema.pattern} {schema.pattern_descriptor && <>({schema.pattern_descriptor})</>}</div>}
      {schema.examples && schema.examples.length > 1 && <div>examples: <ul>
        {schema.examples.map((example, i) => <li key={i}>{example}</li>)}
        </ul></div>}
      {schema.examples && schema.examples.length === 1 && <div>example: {schema.examples[0]}</div>}
      {schema.description && <div><TextWithHTML text={schema.description} /></div>}
      {schema.type === "object" && schema.properties && <JSONSchemaObject schema={schema} />}
      {schema.type === "object" && schema.oneOf && <JSONSchemaOneOf schema={schema} />}
      {schema.type === "array" && <JSONSchemaProperty propertyKey="items[x]" schema={schema.items} />}
    </div>
  </div>
}
