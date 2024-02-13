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
    <div class={styles.grid}>
      <div class={className(styles.headerItem, styles.tableHeader)}>
        Field
      </div>
      <div class={className(styles.headerItem, styles.tableHeader)}>
        Type
      </div>
      <div class={className(styles.headerItem, styles.tableHeader)}>
        Property name
      </div>
      <JSONSchemaObject schema={props.schema} />
    </div>
  </div>
}

function getOrderedProperties(schema) {
  if (!schema.properties) {
    return [];
  }
  const requiredProperties = new Set(schema.required || []);
  return Object.entries(schema.properties).sort(([a], [b]) => {
    // Sort required properties first, then respect the order of the schema
    if (requiredProperties.has(a) && !requiredProperties.has(b)) {
      return -1;
    }
    else if (requiredProperties.has(b) && !requiredProperties.has(a)) {
      return 1;
    }
    else {
      return 0;
    }
  });
}

function JSONSchemaObject(props) {
  const requiredProperties = new Set(props.schema.required || []);
  return <>
    {getOrderedProperties(props.schema).map(([key, schema]) => {
      return <JSONSchemaProperty key={key} propertyKey={key} schema={schema} required={requiredProperties.has(key)} depth={props.depth} />
    })}
  </>
}

function JSONSchemaOneOf(props) {
  return <>
    <ul className={styles.contents}>
      {props.schema.oneOf.map((schema, i) => {
        return <li key={i} className={styles.contents}>
          <JSONSchemaProperty schema={schema} depth={props.depth} />
        </li>
      })}
    </ul>
  </>
}

function isOneOf(schema) {
  return schema.type === "object" && schema.oneOf;
}

function isObjectArray(schema) {
  return schema.type === "array" && schema.items && schema.items.type === "object";
}

function showCollapsible(schema) {
  return (schema.type === "object" && schema.properties) || showDescription(schema)
}

function showDescription(schema) {
  return typeof schema.default !== "undefined" || schema.pattern || schema.examples || schema.description || isOneOf(schema) || (schema.type === "array" && schema.items && schema.items.type === "object");
}

function getIndentStyle(depth) {
  return {
    paddingLeft: `${depth * 13}px`
  };
}

function getType(schema) {
  if (schema.const) {
    return JSON.stringify(schema.const);
  }
  if (schema.type === "array" && schema.items) {
    return `${schema.type}<${schema.items.type}>`;
  }
  return schema.type;
}

function JSONSchemaProperty({ propertyKey, schema, required, depth = 0 }) {
  const newDepth = depth + 1;
  const fieldName = <>
    <div>{schema.title || propertyKey}</div>
    {required && <div className={styles.tag}>required</div>}
  </>;
  const typeAndPropertyName = <>
    <div className={styles.headerItem}>
      {getType(schema)}
    </div>
    <div className={styles.headerItem}>
      {propertyKey && <div>{propertyKey}</div>}
    </div>
  </>;
  if (showCollapsible(schema)) {
    return <Disclosure initiallyOpen={false}>
      {({ open }) => (
        <>
          <Disclosure.Button className={className(styles.headerItem, styles.clickable, styles.propertyName)} style={getIndentStyle(newDepth)}>
            <div className={className({ [styles.open]: open })}>›</div>
            {fieldName}
          </Disclosure.Button>
          {typeAndPropertyName}
          <Disclosure.Panel className={styles.contents}>
            {showDescription(schema) && <Description schema={schema} style={getIndentStyle(newDepth + 1)} />}
            {schema.type === "object" && schema.oneOf && <JSONSchemaOneOf schema={schema} depth={newDepth} />}
            {schema.type === "object" && schema.properties && <JSONSchemaObject schema={schema} depth={newDepth} />}
            {schema.type === "array" && <JSONSchemaObject schema={schema.items} depth={newDepth} />}
          </Disclosure.Panel>
        </>)}
    </Disclosure>
  } else {
    return <>
      <div className={className(styles.headerItem, styles.propertyName)} style={getIndentStyle(newDepth)}>
        {fieldName}
      </div>
      {typeAndPropertyName}
    </>
  }
}

function Description({ schema, style }) {
  return <div className={styles.descriptionItem} style={style}>
  {(typeof schema.default !== "undefined" && !schema.const) && <div>Default: <pre>{JSON.stringify(schema.default, null, 2)}</pre></div>}
  {schema.const && <div>Constant value: <pre>{JSON.stringify(schema.const, null, 2)}</pre></div>}
  {schema.pattern && <div>Pattern{schema.pattern_descriptor && <> ({schema.pattern_descriptor})</>}: <pre>{schema.pattern}</pre></div>}
  {(schema.examples && schema.examples.length > 1) && <div>Examples: <ul>
    {schema.examples.map((example, i) => <li key={i}><pre>{JSON.stringify(example)}</pre></li>)}
  </ul></div>}
  {(schema.examples && schema.examples.length === 1) && <div>Example: <pre>{JSON.stringify(schema.examples[0])}</pre></div>}
  {schema.description && <div><TextWithHTML text={schema.description} /></div>}
  {isOneOf(schema) &&
    <Heading as="h5" className={styles.oneOfHeader}>One of:</Heading>}
  {isObjectArray(schema) && <Heading as="h5" className={styles.oneOfHeader}>Item properties:</Heading>}
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
