import React from "react";
import { JSONSchemaFaker } from "json-schema-faker";
import CodeBlock from '@theme/CodeBlock';


export const AirbyteLibExample = ({
  specJSON,
  connector
}) => {
  const spec = JSON.parse(specJSON);
  const fakeConfig = JSONSchemaFaker.generate(spec);
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
).read_all()

for record in result.cache.streams["my_stream:name"]:
  print(record)`} </CodeBlock>
    <p>You can find more information in the airbyte_lib quickstart guide.</p>
  </>;
};
