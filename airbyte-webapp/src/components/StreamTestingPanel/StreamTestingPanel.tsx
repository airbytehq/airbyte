import { useIntl } from "react-intl";

import { useReadStream } from "services/connectorBuilder/ConnectorBuilderApiService";
import { useConnectorBuilderState } from "services/connectorBuilder/ConnectorBuilderStateService";

import { ResultDisplay } from "./ResultDisplay";
import { StreamSelector } from "./StreamSelector";
import styles from "./StreamTestingPanel.module.scss";
import { TestControls } from "./TestControls";

export const StreamTestingPanel: React.FC<unknown> = () => {
  const { formatMessage } = useIntl();
  const { jsonManifest, selectedStream, configJson } = useConnectorBuilderState();
  const { data: streamReadData, refetch: readStream } = useReadStream({
    manifest: jsonManifest,
    stream: selectedStream.name,
    config: configJson,
  });

  return (
    <div className={styles.container}>
      <StreamSelector className={styles.streamSelector} />
      <TestControls
        className={styles.testControls}
        onClickTest={() => {
          readStream();
        }}
      />
      {streamReadData && streamReadData.slices.length !== 0 ? (
        <ResultDisplay className={styles.resultDisplay} streamRead={streamReadData} />
      ) : (
        <div className={styles.placeholder}>{formatMessage({ id: "connectorBuilder.resultsPlaceholder" })}</div>
      )}
    </div>
  );
};
