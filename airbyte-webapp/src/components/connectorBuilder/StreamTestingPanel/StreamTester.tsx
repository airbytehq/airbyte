import { faWarning } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useEffect, useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";

import { RotateIcon } from "components/icons/RotateIcon";
import { Button } from "components/ui/Button";
import { ResizablePanels } from "components/ui/ResizablePanels";
import { Spinner } from "components/ui/Spinner";
import { Text } from "components/ui/Text";
import { Tooltip } from "components/ui/Tooltip";

import { useReadStream } from "services/connectorBuilder/ConnectorBuilderApiService";
import { useConnectorBuilderState } from "services/connectorBuilder/ConnectorBuilderStateService";

import { LogsDisplay } from "./LogsDisplay";
import { ResultDisplay } from "./ResultDisplay";
import styles from "./StreamTester.module.scss";

export const StreamTester: React.FC = () => {
  const { formatMessage } = useIntl();
  const { jsonManifest, configJson, yamlIsValid, streams, testStreamIndex } = useConnectorBuilderState();
  const {
    data: streamReadData,
    refetch: readStream,
    isError,
    error,
    isFetching,
  } = useReadStream({
    manifest: jsonManifest,
    stream: streams[testStreamIndex]?.name,
    config: configJson,
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

  const testButton = (
    <Button
      full
      size="sm"
      onClick={() => {
        readStream();
      }}
      disabled={!yamlIsValid}
      icon={
        yamlIsValid ? (
          <div>
            <RotateIcon width={styles.testIconHeight} height={styles.testIconHeight} />
          </div>
        ) : (
          <FontAwesomeIcon icon={faWarning} />
        )
      }
    >
      <Text className={styles.testButtonText} size="sm" bold>
        <FormattedMessage id="connectorBuilder.testButton" />
      </Text>
    </Button>
  );

  return (
    <div className={styles.container}>
      <Text className={styles.url} size="lg">
        {streams[testStreamIndex]?.url}
      </Text>
      {yamlIsValid ? (
        testButton
      ) : (
        <Tooltip control={testButton} containerClassName={styles.testButtonTooltipContainer}>
          <FormattedMessage id="connectorBuilder.invalidYamlTest" />
        </Tooltip>
      )}
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
