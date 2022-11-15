import { useState } from "react";
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
  const [logsFlex, setLogsFlex] = useState(0);

  const handleLogsTitleClick = () => {
    // expand to 50% if it is currently minimized, otherwise minimize it
    setLogsFlex((prevFlex) => (prevFlex < 0.06 ? 0.5 : 0));
  };

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
            children: <ResultDisplay slices={streamReadData.slices} />,
            minWidth: 120,
          }}
          secondPanel={{
            className: styles.logsContainer,
            children: <LogsDisplay logs={streamReadData.logs} onTitleClick={handleLogsTitleClick} />,
            minWidth: 30,
            flex: logsFlex,
            onStopResize: (newFlex) => {
              if (newFlex) {
                setLogsFlex(newFlex);
              }
            },
          }}
          hideSecondPanel={streamReadData.logs.length === 0}
        />
      ) : (
        <div className={styles.placeholder}>{formatMessage({ id: "connectorBuilder.resultsPlaceholder" })}</div>
      )}
    </div>
  );
};
