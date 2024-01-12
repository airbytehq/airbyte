import React from "react";
import styles from "./SpecSchema.module.css";
import sanitizeHtml from "sanitize-html";
import { Disclosure } from "@headlessui/react";
import Heading from '@theme/Heading';
import className from 'classnames';

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
    <ul className={styles.oneOfList}>
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
  const isPrimitive = schema.type !== "object" && schema.type !== "array" && !schema.description && !schema.pattern && !schema.examples;
  if (isPrimitive) {
    return <div className={styles.block}>
      <div className={styles.header}>
        {propertyKey && <div className={styles.propertyName}>{propertyKey}</div>}
        {schema.title && <div>{schema.title}</div>}
        {required && <div className={styles.tag}>required</div>}
        <div className={styles.tag}>type: {schema.type}</div>
        {schema.const && <div className={styles.tag}>constant value: {JSON.stringify(schema.const)}</div>}
      </div></div>
  } else {
    return <Disclosure initiallyOpen={false}>
      {({ open }) => (
        <div className={styles.block}>
          <Disclosure.Button className={className(styles.header, styles.clickable)}>
            <div className={className({ [styles.open]: open })}>›</div>
            {propertyKey && <div className={styles.propertyName}>{propertyKey}</div>}
            {schema.title && <div>{schema.title}</div>}
            {required && <div className={styles.tag}>required</div>}
            {schema.const && <div className={styles.tag}>constant value: {JSON.stringify(schema.const)}</div>}
          </Disclosure.Button>
          <Disclosure.Panel>
            <div className={styles.propertyDocumentation}>
              <div>Type: {schema.type}</div>
              {(typeof schema.default !== "undefined" && !schema.const) && <div>Default: <pre>{JSON.stringify(schema.default, null, 2)}</pre></div>}
              {schema.pattern && <div>Pattern{schema.pattern_descriptor && <> ({schema.pattern_descriptor})</>}: <pre>{schema.pattern}</pre></div>}
              {(schema.examples && schema.examples.length > 1) && <div>Examples: <ul>
                {schema.examples.map((example, i) => <li key={i}><pre>{JSON.stringify(example)}</pre></li>)}
              </ul></div>}
              {(schema.examples && schema.examples.length === 1) && <div>Example: <pre>{JSON.stringify(schema.examples[0])}</pre></div>}
              {schema.description && <div><TextWithHTML text={schema.description} /></div>}
              {schema.type === "object" && schema.oneOf && <JSONSchemaOneOf schema={schema} />}
              {schema.type === "object" && schema.properties && <JSONSchemaObject schema={schema} />}
              {schema.type === "array" && <JSONSchemaProperty propertyKey="items[x]" schema={schema.items} />}
            </div>
          </Disclosure.Panel>
        </div>)}
    </Disclosure>
  }
}
