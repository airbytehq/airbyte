import { useMemo, useState } from "react";
import { FormattedMessage } from "react-intl";

import { Button } from "components/ui/Button";
import { Heading } from "components/ui/Heading";
import { Text } from "components/ui/Text";
import { Tooltip } from "components/ui/Tooltip";

import { useDestinationDefinitionList } from "services/connector/DestinationDefinitionService";
import { useSourceDefinitionList } from "services/connector/SourceDefinitionService";
import { getIcon } from "utils/imageUtils";
import { links } from "utils/links";

import { AirbyteIllustration } from "./AirbyteIllustration";
import styles from "./ConnectionOnboarding.module.scss";
import { ReactComponent as PlusIcon } from "./plusIcon.svg";

interface ConnectionOnboardingProps {
  onCreate: (sourceConnectorTypeId?: string) => void;
}

export const ConnectionOnboarding: React.FC<ConnectionOnboardingProps> = ({ onCreate }) => {
  // TODO: Those should be parallelized
  const { sourceDefinitions } = useSourceDefinitionList();
  const { destinationDefinitions } = useDestinationDefinitionList();

  const [highlightedSource, setHighlightedSource] = useState<0 | 1 | 2 | 3>(1);
  const [highlightedDestination, setHighlightedDestination] = useState<0 | 1 | 2 | 3>(0);

  const sourceIds = useMemo(
    () => [
      "e7778cfc-e97c-4458-9ecb-b4f2bba8946c",
      "71607ba1-c0ac-4799-8049-7f4b90dd50f7",
      "6acf6b55-4f1e-4fca-944e-1a3caef8aba8",
    ],
    []
  );

  const destinationIds = useMemo(
    () => [
      "424892c4-daac-4491-b35d-c6688ba547ba",
      "25c5221d-dce2-4163-ade9-739ef790f503",
      "22f6c74f-5699-40ff-833c-4a879ea40133",
      "f7a7d195-377f-cf5b-70a5-be6b819019dc",
    ],
    []
  );

  const sources = useMemo(
    () => sourceIds.map((id) => sourceDefinitions.find((def) => def.sourceDefinitionId === id)),
    [sourceDefinitions, sourceIds]
  );

  const destinations = useMemo(
    () => destinationIds.map((id) => destinationDefinitions.find((def) => def.destinationDefinitionId === id)),
    [destinationDefinitions, destinationIds]
  );

  return (
    <div className={styles.container}>
      <Heading as="h2" size="lg" centered className={styles.heading}>
        <FormattedMessage id="connection.onboarding.title" />
      </Heading>
      <div className={styles.connectors}>
        <Text bold as="div" className={styles.sourcesTitle}>
          <Tooltip control={<FormattedMessage id="connection.onboarding.sources" />}>
            <FormattedMessage id="connection.onboarding.sourcesDescription" />
          </Tooltip>
        </Text>
        <div className={styles.sources}>
          {sources.map((source, index) => (
            <Tooltip
              placement="right"
              control={
                <button
                  className={styles.connectorButton}
                  onClick={() => onCreate(source?.sourceDefinitionId)}
                  onMouseEnter={() => setHighlightedSource(index as 0 | 1 | 2)}
                >
                  <div className={styles.connectorIcon}>{getIcon(source?.icon)}</div>
                </button>
              }
            >
              <FormattedMessage id="connection.onboarding.addSource" values={{ source: source?.name }} />
            </Tooltip>
          ))}

          <Tooltip
            placement="right"
            control={
              <button
                className={styles.connectorButton}
                onClick={() => onCreate()}
                onMouseEnter={() => setHighlightedSource(3)}
              >
                <PlusIcon className={styles.moreIcon} />
              </button>
            }
          >
            <FormattedMessage
              id="connection.onboarding.moreSources"
              values={{ count: Math.floor(sourceDefinitions.length / 10) * 10 }}
            />
          </Tooltip>
        </div>
        <div className={styles.airbyte} aria-hidden="true">
          <AirbyteIllustration sourceHighlighted={highlightedSource} destinationHighlighted={highlightedDestination} />
        </div>
        <Text bold as="div" className={styles.destinationsTitle}>
          <Tooltip control={<FormattedMessage id="connection.onboarding.destinations" />}>
            <FormattedMessage id="connection.onboarding.destinationsDescription" />
          </Tooltip>
        </Text>
        <div className={styles.destinations}>
          {destinations.map((destination, index) => (
            <Tooltip
              placement="right"
              control={
                <button
                  className={styles.connectorButton}
                  // onMouseEnter doesn't trigger on disabled buttons in React
                  // https://github.com/facebook/react/issues/10109
                  // Thus we just disable it via aria-disabled and make it non focusable via tabindex
                  onMouseEnter={() => setHighlightedDestination(index as 0 | 1 | 2 | 3)}
                  aria-disabled="true"
                  tabIndex={-1}
                >
                  <div className={styles.connectorIcon}>{getIcon(destination?.icon)}</div>
                </button>
              }
            >
              <FormattedMessage id="connection.onboarding.addDestination" values={{ destination: destination?.name }} />
            </Tooltip>
          ))}
        </div>
      </div>
      <div className={styles.footer}>
        <Button onClick={() => onCreate()} size="lg" data-id="new-connection">
          <FormattedMessage id="connection.onboarding.createFirst" />
        </Button>
        <FormattedMessage
          tagName="span"
          id="connection.onboarding.demoInstance"
          values={{
            demoLnk: (children: React.ReactNode) => (
              <a href={links.demoLink} target="_blank" rel="noreferrer noopener" className={styles.demoLink}>
                {children}
              </a>
            ),
          }}
        />
      </div>
    </div>
  );
};
