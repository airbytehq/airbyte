import { useReadStream } from "services/connectorBuilder/ConnectorBuilderApiService";
import { useConnectorBuilderState } from "services/connectorBuilder/ConnectorBuilderStateService";

import { ResultDisplay } from "./ResultDisplay";
import { StreamSelector } from "./StreamSelector";
import styles from "./StreamTestingPanel.module.scss";
import { TestControls } from "./TestControls";

export const StreamTestingPanel: React.FC<unknown> = () => {
  const { jsonManifest, selectedStream, configJson } = useConnectorBuilderState();
  const { data: streamReadData, refetch: readStream } = useReadStream({
    manifest: jsonManifest,
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
      {streamReadData && <ResultDisplay streamRead={streamReadData} />}
    </div>
  );
};
