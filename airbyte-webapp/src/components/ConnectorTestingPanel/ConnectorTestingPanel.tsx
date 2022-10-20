import { useReadStream } from "services/connector-builder/ConnectorBuilderApiService";
import { useConnectorBuilderState } from "services/connector-builder/ConnectorBuilderStateService";

import styles from "./ConnectorTestingPanel.module.scss";
import { ResultDisplay } from "./ResultDisplay";
import { StreamSelector } from "./StreamSelector";
import { TestControls } from "./TestControls";

export const ConnectorTestingPanel: React.FC<unknown> = () => {
  const { jsonDefinition, selectedStream, configJson } = useConnectorBuilderState();
  const { data: streamReadData, refetch: readStream } = useReadStream({
    connectorDefinition: jsonDefinition,
    stream: selectedStream.name,
    config: configJson,
  });

  return (
    <div className={styles.container}>
      <StreamSelector />
      <TestControls
        onClickTest={() => {
          readStream();
        }}
      />
      <ResultDisplay data={streamReadData ?? { slices: [] }} />
    </div>
  );
};
