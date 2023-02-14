import { faClose } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useEffect, useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { useLocalStorage } from "react-use";

import { Button } from "components/ui/Button";
import { Callout } from "components/ui/Callout";
import { FlexContainer, FlexItem } from "components/ui/Flex";
import { ResizablePanels } from "components/ui/ResizablePanels";
import { Spinner } from "components/ui/Spinner";
import { Text } from "components/ui/Text";

import { Action, Namespace } from "core/analytics";
import { StreamsListReadStreamsItem } from "core/request/ConnectorBuilderClient";
import { useAnalyticsService } from "hooks/services/Analytics";
import { useConnectorBuilderTestState } from "services/connectorBuilder/ConnectorBuilderStateService";
import { links } from "utils/links";

import { LogsDisplay } from "./LogsDisplay";
import { ResultDisplay } from "./ResultDisplay";
import { StreamTestButton } from "./StreamTestButton";
import styles from "./StreamTester.module.scss";

export const StreamTester: React.FC<{
  hasTestInputJsonErrors: boolean;
  setTestInputOpen: (open: boolean) => void;
}> = ({ hasTestInputJsonErrors, setTestInputOpen }) => {
  const { formatMessage } = useIntl();
  const {
    streams,
    testStreamIndex,
    isFetchingStreamList,
    streamListErrorMessage,
    streamRead: {
      data: streamReadData,
      refetch: readStream,
      isError,
      error,
      isFetching,
      isFetchedAfterMount,
      dataUpdatedAt,
      errorUpdatedAt,
    },
  } = useConnectorBuilderTestState();
  const [showLimitWarning, setShowLimitWarning] = useLocalStorage<boolean>("connectorBuilderLimitWarning", true);

  const streamName = streams[testStreamIndex]?.name;

  const analyticsService = useAnalyticsService();

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

  useEffect(() => {
    // This will only be true if the data was manually refetched by the user clicking the Test button,
    // so the analytics events won't fire just from the user switching between streams, as desired
    if (isFetchedAfterMount) {
      if (errorMessage) {
        analyticsService.track(Namespace.CONNECTOR_BUILDER, Action.STREAM_TEST_FAILURE, {
          actionDescription: "Stream test failed",
          stream_name: streamName,
          error_message: errorMessage,
        });
      } else {
        analyticsService.track(Namespace.CONNECTOR_BUILDER, Action.STREAM_TEST_SUCCESS, {
          actionDescription: "Stream test succeeded",
          stream_name: streamName,
        });
      }
    }
  }, [analyticsService, errorMessage, isFetchedAfterMount, streamName, dataUpdatedAt, errorUpdatedAt]);

  const currentStream = streams[testStreamIndex] as StreamsListReadStreamsItem | undefined;
  return (
    <div className={styles.container}>
      {currentStream && (
        <Text className={styles.url} centered size="lg">
          {currentStream.url}
        </Text>
      )}
      {!currentStream && isFetchingStreamList && (
        <Text size="lg" centered>
          <FormattedMessage id="connectorBuilder.loadingStreamList" />
        </Text>
      )}
      {!currentStream && streamListErrorMessage && (
        <Text size="lg" centered>
          <FormattedMessage id="connectorBuilder.streamListUrlError" />
        </Text>
      )}

      <StreamTestButton
        readStream={() => {
          readStream();
          analyticsService.track(Namespace.CONNECTOR_BUILDER, Action.STREAM_TEST, {
            actionDescription: "Stream test initiated",
            stream_name: streamName,
          });
        }}
        hasTestInputJsonErrors={hasTestInputJsonErrors}
        hasStreamListErrors={Boolean(streamListErrorMessage)}
        setTestInputOpen={setTestInputOpen}
      />

      {streamListErrorMessage !== undefined && (
        <div className={styles.listErrorDisplay}>
          <Text>
            <FormattedMessage id="connectorBuilder.couldNotDetectStreams" />
          </Text>
          <Text bold>{streamListErrorMessage}</Text>
          <Text>
            <FormattedMessage
              id="connectorBuilder.ensureProperYaml"
              values={{
                a: (node: React.ReactNode) => (
                  <a href={links.lowCodeYamlDescription} target="_blank" rel="noreferrer">
                    {node}
                  </a>
                ),
              }}
            />
          </Text>
        </div>
      )}
      {isFetching && (
        <div className={styles.fetchingSpinner}>
          <Spinner />
        </div>
      )}
      {!isFetching && streamReadData && streamReadData.test_read_limit_reached && showLimitWarning && (
        <Callout>
          <FlexItem grow>
            <FlexContainer alignItems="center">
              <FlexItem grow>
                <FormattedMessage id="connectorBuilder.streamTestLimitReached" />
              </FlexItem>
              <Button
                onClick={() => {
                  setShowLimitWarning(false);
                }}
                variant="clear"
                icon={<FontAwesomeIcon icon={faClose} />}
              />
            </FlexContainer>
          </FlexItem>
        </Callout>
      )}
      {!isFetching && (streamReadData !== undefined || errorMessage !== undefined) && (
        <ResizablePanels
          className={styles.resizablePanelsContainer}
          orientation="horizontal"
          firstPanel={{
            children: (
              <>
                {streamReadData !== undefined && !isError && (
                  <ResultDisplay slices={streamReadData.slices} inferredSchema={streamReadData.inferred_schema} />
                )}
              </>
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
