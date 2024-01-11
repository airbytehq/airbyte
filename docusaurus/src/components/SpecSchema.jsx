import React from "react";
import styles from "./SpecSchema.module.css";
import sanitizeHtml from "sanitize-html";
import { Disclosure } from "@headlessui/react";
import Heading from '@theme/Heading';

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
    {/* <pre>{JSON.stringify(props.schema, null, 2)}</pre> */}
    <Heading as="h4">Config fields reference</Heading>
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
    <Heading as="h5">One of:</Heading>
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
  return <Disclosure initiallyOpen={false}><div className={styles.block}>
    <Disclosure.Button className={styles.header}>
      {propertyKey && <div className={styles.propertyName}>{propertyKey}</div>}
      {schema.title && <div>{schema.title}</div>}
      {required && <div className={styles.tag}>required</div>}
      {schema.const && <div className={styles.tag}>constant value: {schema.default}</div>}
    </Disclosure.Button>
    <Disclosure.Panel>
      <div>type: {schema.type}</div>
      {schema.default && !schema.const && <div>default: <pre>{JSON.stringify(schema.default, null, 2)}</pre></div>}
      {schema.pattern && <div>pattern: {schema.pattern} {schema.pattern_descriptor && <>({schema.pattern_descriptor})</>}</div>}
      {schema.examples && schema.examples.length > 1 && <div>examples: <ul>
        {schema.examples.map((example, i) => <li key={i}>{example}</li>)}
      </ul></div>}
      {schema.examples && schema.examples.length === 1 && <div>example: {schema.examples[0]}</div>}
      {schema.description && <div><TextWithHTML text={schema.description} /></div>}
      {(schema.type === "object" && (schema.properties || schema.oneOf)) || schema.type === "array" && <Heading as="h5">Sub-properties</Heading>}
      {schema.type === "object" && schema.properties && <JSONSchemaObject schema={schema} />}
      {schema.type === "object" && schema.oneOf && <JSONSchemaOneOf schema={schema} />}
      {schema.type === "array" && <JSONSchemaProperty propertyKey="items[x]" schema={schema.items} />}
    </Disclosure.Panel>
  </div></Disclosure>
}
