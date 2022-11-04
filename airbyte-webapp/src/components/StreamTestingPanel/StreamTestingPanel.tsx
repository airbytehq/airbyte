import { useIntl } from "react-intl";

import { ResizablePanels } from "components/ui/ResizablePanels";

import { useReadStream } from "services/connectorBuilder/ConnectorBuilderApiService";
import { useConnectorBuilderState } from "services/connectorBuilder/ConnectorBuilderStateService";

import { LogsDisplay } from "./LogsDisplay";
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
        <ResizablePanels
          className={styles.resizablePanelsContainer}
          orientation="horizontal"
          firstPanel={{
            children: <ResultDisplay streamRead={streamReadData} />,
            minWidth: 120,
          }}
          secondPanel={{
            className: styles.logsContainer,
            children: <LogsDisplay logs={streamReadData.logs} />,
            minWidth: 30,
            flex: 0,
          }}
          hideSecondPanel={streamReadData.logs.length === 0}
        />
      ) : (
        <div className={styles.placeholder}>{formatMessage({ id: "connectorBuilder.resultsPlaceholder" })}</div>
      )}
    </div>
  );
};
