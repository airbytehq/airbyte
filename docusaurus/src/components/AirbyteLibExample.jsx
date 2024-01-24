import React, { useMemo } from "react";
import { JSONSchemaFaker } from "json-schema-faker";
import CodeBlock from '@theme/CodeBlock';
import Heading from '@theme/Heading';


export const AirbyteLibExample = ({
  specJSON,
  connector,
}) => {
  const spec = useMemo(() => JSON.parse(specJSON), [specJSON]);
  const fakeConfig = useMemo(() => JSONSchemaFaker.generate(spec), [spec]);
  return <>
    <p>
      Install the Python library via:
    </p>
    <CodeBlock
        language="bash">{"pip install airbyte-lib"}</CodeBlock>
    <p>Then, execute a sync by loading the connector like this:</p>
    <CodeBlock
      language="python"
    >{`import airbyte_lib as ab

config = ${JSON.stringify(fakeConfig, null, 2)}

result = ab.get_connector(
    "${connector}",
    config=config,
).read()

for record in result.cache.streams["my_stream:name"]:
  print(record)`} </CodeBlock>
    <p>You can find more information in the airbyte_lib quickstart guide.</p>
  </>;
};
