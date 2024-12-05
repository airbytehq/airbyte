import React, { useMemo } from "react";
import { JSONSchemaFaker } from "json-schema-faker";
import CodeBlock from '@theme/CodeBlock';

/**
 * Generate a fake config based on the spec.
 *
 * As our specs are not 100% consistent, errors may occur.
 * Try to generate a few times before giving up.
 */
function generateFakeConfig(spec) {
  let tries = 5;
  while (tries > 0) {
    try {
      return JSON.stringify(JSONSchemaFaker.generate(spec), null, 2)
    }
    catch (e) {
      tries--;
    }
  }
  return "{ ... }";
}

export const PyAirbyteExample = ({
  specJSON,
  connector,
}) => {
  const spec = useMemo(() => JSON.parse(specJSON), [specJSON]);
  const fakeConfig = useMemo(() => generateFakeConfig(spec), [spec]);
  return <>
    <p>
      Install the Python library via:
    </p>
    <CodeBlock
        language="bash">{"pip install airbyte"}</CodeBlock>
    <p>Then, execute a sync by loading the connector like this:</p>
    <CodeBlock
      language="python"
    >{`import airbyte as ab

config = ${fakeConfig}

result = ab.get_source(
    "${connector}",
    config=config,
).read()

for record in result.cache.streams["my_stream:name"]:
  print(record)`} </CodeBlock>
    <p>You can find more information in the airbyte_lib quickstart guide.</p>
  </>;
};
