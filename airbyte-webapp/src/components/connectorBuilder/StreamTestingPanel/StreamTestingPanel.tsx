import React from "react";
import { FormattedMessage } from "react-intl";

import { Heading } from "components/ui/Heading";
import { Spinner } from "components/ui/Spinner";
import { Text } from "components/ui/Text";

import { useConnectorBuilderState } from "services/connectorBuilder/ConnectorBuilderStateService";
import { links } from "utils/links";

import { ConfigMenu } from "./ConfigMenu";
import { StreamSelector } from "./StreamSelector";
import { StreamTester } from "./StreamTester";
import styles from "./StreamTestingPanel.module.scss";

export const StreamTestingPanel: React.FC<unknown> = () => {
  const { jsonManifest, streamListErrorMessage, yamlEditorIsMounted } = useConnectorBuilderState();

  if (!yamlEditorIsMounted) {
    return (
      <div className={styles.loadingSpinner}>
        <Spinner />
      </div>
    );
  }

  const hasStreams = jsonManifest.streams?.length > 0;

  return (
    <div className={styles.container}>
      {!hasStreams && (
        <div className={styles.addStreamMessage}>
          <Heading as="h2" className={styles.addStreamHeading}>
            <FormattedMessage id="connectorBuilder.noStreamsMessage" />
          </Heading>
          <img className={styles.logo} alt="" src="/images/octavia/pointing.svg" width={102} />
        </div>
      )}
      {hasStreams && streamListErrorMessage === undefined && (
        <>
          <ConfigMenu className={styles.configButton} />
          <div className={styles.selectAndTestContainer}>
            <StreamSelector className={styles.streamSelector} />
            <StreamTester />
          </div>
        </>
      )}
      {hasStreams && streamListErrorMessage !== undefined && (
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
    </div>
  );
};
