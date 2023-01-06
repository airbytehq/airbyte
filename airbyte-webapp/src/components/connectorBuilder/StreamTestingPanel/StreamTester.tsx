import { useEffect, useState } from "react";
import { useIntl } from "react-intl";

import { ResizablePanels } from "components/ui/ResizablePanels";
import { Spinner } from "components/ui/Spinner";
import { Text } from "components/ui/Text";

import { useReadStream } from "services/connectorBuilder/ConnectorBuilderApiService";
import {
  useConnectorBuilderTestState,
  useConnectorBuilderFormState,
} from "services/connectorBuilder/ConnectorBuilderStateService";

import { LogsDisplay } from "./LogsDisplay";
import { ResultDisplay } from "./ResultDisplay";
import { StreamTestButton } from "./StreamTestButton";
import styles from "./StreamTester.module.scss";

export const StreamTester: React.FC<{
  hasTestInputJsonErrors: boolean;
  setTestInputOpen: (open: boolean) => void;
}> = ({ hasTestInputJsonErrors, setTestInputOpen }) => {
  const { formatMessage } = useIntl();
  const { jsonManifest } = useConnectorBuilderFormState();
  const { streams, testInputJson, testStreamIndex } = useConnectorBuilderTestState();
  const {
    data: streamReadData,
    refetch: readStream,
    isError,
    error,
    isFetching,
  } = useReadStream({
    manifest: jsonManifest,
    stream: streams[testStreamIndex]?.name,
    config: testInputJson,
  });

  const [logsFlex, setLogsFlex] = useState(0);
  const handleLogsTitleClick = () => {
    // expand to 50% if it is currently minimized, otherwise minimize it
    setLogsFlex((prevFlex) => (prevFlex < 0.06 ? 0.5 : 0));
  };

  const unknownErrorMessage = formatMessage({ id: "connectorBuilder.unknownError" });
  const errorMessage = isError
    ? error instanceof Error
      ? error.message || unknownErrorMessage
      : unknownErrorMessage
    : undefined;

  useEffect(() => {
    if (isError) {
      setLogsFlex(1);
    } else {
      setLogsFlex(0);
    }
  }, [isError]);

  return (
    <div className={styles.container}>
      <Text className={styles.url} size="lg">
        {streams[testStreamIndex]?.url}
      </Text>

      <StreamTestButton
        readStream={readStream}
        hasTestInputJsonErrors={hasTestInputJsonErrors}
        setTestInputOpen={setTestInputOpen}
      />

      {isFetching && (
        <div className={styles.fetchingSpinner}>
          <Spinner />
        </div>
      )}
      {!isFetching && (streamReadData !== undefined || errorMessage !== undefined) && (
        <ResizablePanels
          className={styles.resizablePanelsContainer}
          orientation="horizontal"
          firstPanel={{
            children: (
              <>{streamReadData !== undefined && !isError && <ResultDisplay slices={streamReadData.slices} />}</>
            ),
            minWidth: 80,
          }}
          secondPanel={{
            className: styles.logsContainer,
            children: (
              <LogsDisplay logs={streamReadData?.logs ?? []} error={errorMessage} onTitleClick={handleLogsTitleClick} />
            ),
            minWidth: 30,
            flex: logsFlex,
            onStopResize: (newFlex) => {
              if (newFlex) {
                setLogsFlex(newFlex);
              }
            },
          }}
        />
      )}
    </div>
  );
};
