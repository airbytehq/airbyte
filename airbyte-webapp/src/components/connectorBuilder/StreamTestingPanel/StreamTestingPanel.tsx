import React from "react";
import { FormattedMessage } from "react-intl";

import { Spinner } from "components/ui/Spinner";
import { Text } from "components/ui/Text";

import { useConnectorBuilderState } from "services/connectorBuilder/ConnectorBuilderStateService";
import { links } from "utils/links";

import { ConfigMenu } from "./ConfigMenu";
import { StreamSelector } from "./StreamSelector";
import { StreamTester } from "./StreamTester";
import styles from "./StreamTestingPanel.module.scss";

export const StreamTestingPanel: React.FC<unknown> = () => {
  const { selectedStream, streams, streamListErrorMessage, yamlEditorIsMounted } = useConnectorBuilderState();

  if (!yamlEditorIsMounted) {
    return (
      <div className={styles.loadingSpinner}>
        <Spinner />
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <ConfigMenu className={styles.configButton} />
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
      {streamListErrorMessage === undefined && selectedStream !== undefined && (
        <div className={styles.selectAndTestContainer}>
          <StreamSelector className={styles.streamSelector} streams={streams} selectedStream={selectedStream} />
          <StreamTester selectedStream={selectedStream} />
        </div>
      )}
    </div>
  );
};
