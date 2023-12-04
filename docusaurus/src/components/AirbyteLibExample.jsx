import React from "react";
import { JSONSchemaFaker } from "json-schema-faker";

export const AirbyteLibSourceExample = ({
  specJSON,
  connector
}) => {
  const spec = JSON.parse(specJSON);
    const fakeConfig = JSONSchemaFaker.generate(spec);
    return <>
    <p>
      Install the Python library via: <code>pip install airbyte-lib</code>
    </p>
    <p>Then, execute a sync by loading the connector like this:</p>
    <pre>
      <code>{`import airbyte_lib as ab
import pandas as pb

config = ${JSON.stringify(fakeConfig, null, 2)}

result = ab.sync(
  source=ab.get_connector(
    "${connector}",
    config=config,
  ),
  destination=None,
  install_missing=True,
)

# Records are available via pandas dataframes
data: Dict[any, pb.DataFrame] = sync_result.as_dataframes()`}</code>
</pre>
    <p>You can find more information in the airbyte_lib quickstart guide.</p>
    </>;
  };

export const AirbyteLibDestinationExample = ({
  specJSON,
  connector
}) => {
  const spec = JSON.parse(specJSON);
    const fakeConfig = JSONSchemaFaker.generate(spec);
    return <>
    <p>
      Install the Python library via: <code>pip install airbyte-lib</code>
    </p>
    <p>Then, execute a sync by loading the connector like this:</p>
    <pre>
      <code>{`import airbyte_lib as ab
import pandas as pb

config = ${JSON.stringify(fakeConfig, null, 2)}

result = ab.sync(
  source=ab.source_from_dataframes({"my_df": df}),
  destination=ab.get_connector(
    "${connector}",
    config=config,
  ),
  install_missing=True,
)`}</code>
</pre>
    <p>You can find more information in the airbyte_lib quickstart guide.</p>
    </>;
  };