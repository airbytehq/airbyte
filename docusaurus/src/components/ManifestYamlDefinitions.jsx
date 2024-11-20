import React from 'react';
import schema from "../../../airbyte-cdk/python/airbyte_cdk/sources/declarative/declarative_component_schema.yaml";
import ReactMarkdown from 'react-markdown'
import Heading from '@theme/Heading';

function Description({ text }) {
  if (!text) return null;
  return <ReactMarkdown children={text} />;
}

function Examples({ examples }) {
  if (!examples) return null;
  return <>
    {examples.length === 1 ? "Example:" : "Examples:"}
    {examples.map((example, index) => <pre key={index}>
      {typeof example === "string" ? example : JSON.stringify(example, null, 2)}
    </pre>
    )}
  </>
}

function Name({ name, definition }) {
  const type = definition.type;
  const ref = definition["$ref"] || type === "array" && definition.items && definition.items["$ref"];
  return <>
    {name}{definition.type || ref ? <>{type && <>{" "}<code>{type}</code></>}{ref && <>{" "}<code><a href={`${ref}`}>{ref}</a></code></>}</> : null}
  </>
}

function Definition({ name, definition }) {
  return <React.Fragment>
    <Heading as="h3" id={`/definitions/${name}`}><Name name={name} definition={definition} /></Heading>
    <Description text={definition.description} />
    {definition.properties && <>Properties:
      <ul>
        {Object.entries(definition.properties || {}).filter(([name]) => name !== "type" && name !== "definitions").map(([name, property]) => <li key={name}>
          <Heading as="h4"><Name name={name} definition={property} /></Heading>
          <Description text={property.description} />
          {name === "$parameters" &&
          <Description text={"Set parameters that are inherited to all children. See the [section in the advanced topics](/connector-development/config-based/advanced-topics#parameters) for more details."} />
          }
          {property.anyOf && <>Type: <ul>
            {property.anyOf.map((type, index) => <li key={index}>
              {type["$ref"] && <a href={`${type["$ref"]}`}><code>{type["$ref"]}</code></a>}
              {type.type && <code>{type.type}</code>}
            </li>)}
          </ul><br /></>}
          {property.interpolation_context && <>Available variables:
            <ul>
              {property.interpolation_context.map((variable, index) => <li key={index}>
                <a href={`#/variables/${variable}`}>{variable}</a>
              </li>)}
            </ul><br /></>}
          <Examples examples={property.examples} />
        </li>)}
      </ul></>}
    <Examples examples={definition.examples} />
  </React.Fragment>;
}


export default function ManifestYamlDefinitions() {
  const definitions = Object.entries(schema.definitions);

  return <>
    <Heading as="h2" id="components">Components</Heading>
    <Definition name="DeclarativeSource" definition={schema} />
    {definitions.map(([name, definition]) => <Definition key={name} name={name} definition={definition} />)}
    <Heading as="h2" id="variables">Interpolation variables</Heading>
    <p>All string properties that list out available variables allow <a href="https://jinja.palletsprojects.com/en/3.0.x/templates/#expressions">jinja expressions</a>. They can be used by placing them in double curly braces: <code>{"{{ config.property }}"}</code>. The following variables are available</p>
    {schema.interpolation.variables.map((variable) => <React.Fragment key={variable.title}>
      <Heading as="h3" id={`/variables/${variable.title}`}><Name name={variable.title} definition={variable} /></Heading>
      <Description text={variable.description} />
      <Examples examples={variable.examples} />
    </React.Fragment>)}

    <Heading as="h2" id="macros">Interpolation macros</Heading>
    <p>Besides referencing variables, the following macros can be called as part of <a href="https://jinja.palletsprojects.com/en/3.0.x/templates/#expressions">jinja expressions</a>, for example like this: <code>{"{{ now_utc() }}"}</code>.</p>
    {schema.interpolation.macros.map((macro) => <React.Fragment key={macro.title}>
      <Heading as="h3" id={`/macros/${macro.title}`}>{macro.title}</Heading>
      <Description text={macro.description} />
      {Object.keys(macro.arguments).length > 0 && <>Arguments: <ul>{Object.entries(macro.arguments).map(([name, argument]) => <li key={name}>
        <code>{name}</code>: {argument}
      </li>)}
      </ul></>}
      <Examples examples={macro.examples} />
    </React.Fragment>)}

    <Heading as="h2" id="filters">Interpolation filters</Heading>
    <p>The following filters can be called as part of <a href="https://jinja.palletsprojects.com/en/3.0.x/templates/#expressions">jinja expressions</a>, for example like this: <code>{"{{  1 | string  }}"}</code>.</p>
    {schema.interpolation.filters.map((filter) => <React.Fragment key={filter.title}>
      <Heading as="h3" id={`/filters/${filter.title}`}>{filter.title}</Heading>
      <Description text={filter.description} />
      {Object.keys(filter.arguments).length > 0 && <>Arguments: <ul>{Object.entries(filter.arguments).map(([name, argument]) => <li key={name}>
        <code>{name}</code>: {argument}
      </li>)}
      </ul></>}
      <Examples examples={filter.examples} />
    </React.Fragment>)}
  </>
}
