import { faCircleQuestion } from "@fortawesome/free-regular-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useMemo, useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";

import { Button } from "components/ui/Button";
import { Heading } from "components/ui/Heading";
import { Text } from "components/ui/Text";
import { Tooltip } from "components/ui/Tooltip";

import { useAvailableConnectorDefinitions } from "hooks/domain/connector/useAvailableConnectorDefinitions";
import { useDestinationDefinitionList } from "services/connector/DestinationDefinitionService";
import { useSourceDefinitionList } from "services/connector/SourceDefinitionService";
import { useCurrentWorkspace } from "services/workspaces/WorkspacesService";
import { getIcon } from "utils/imageUtils";
import { links } from "utils/links";

import { AirbyteIllustration } from "./AirbyteIllustration";
import styles from "./ConnectionOnboarding.module.scss";
import { ReactComponent as PlusIcon } from "./plusIcon.svg";

interface ConnectionOnboardingProps {
  onCreate: (sourceConnectorTypeId?: string) => void;
}

export const ConnectionOnboarding: React.FC<ConnectionOnboardingProps> = ({ onCreate }) => {
  const { formatMessage } = useIntl();
  const workspace = useCurrentWorkspace();
  // TODO: Those should be parallelized
  const sourceDefinitions = useAvailableConnectorDefinitions(useSourceDefinitionList().sourceDefinitions, workspace);
  const destinationDefinitions = useAvailableConnectorDefinitions(
    useDestinationDefinitionList().destinationDefinitions,
    workspace
  );

  const [highlightedSource, setHighlightedSource] = useState<0 | 1 | 2 | 3>(1);
  const [highlightedDestination, setHighlightedDestination] = useState<0 | 1 | 2 | 3>(0);

  const sourceIds = useMemo(
    () => [
      "e7778cfc-e97c-4458-9ecb-b4f2bba8946c", // Facebook
      "decd338e-5647-4c0b-adf4-da0e75f5a750", // Postgres
      "71607ba1-c0ac-4799-8049-7f4b90dd50f7", // Google Sheets
    ],
    []
  );

  const destinationIds = useMemo(
    () => [
      "22f6c74f-5699-40ff-833c-4a879ea40133", // BigQuery
      "424892c4-daac-4491-b35d-c6688ba547ba", // Snowflake
      "25c5221d-dce2-4163-ade9-739ef790f503", // Postgres
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

  const moreSourcesTooltip = formatMessage(
    { id: "connection.onboarding.moreSources" },
    { count: Math.floor(sourceDefinitions.length / 10) * 10 }
  );

  const moreDestinationsTooltip = formatMessage(
    { id: "connection.onboarding.moreDestinations" },
    { count: Math.floor(destinationDefinitions.length / 10) * 10 }
  );

  return (
    <div className={styles.container}>
      <Heading as="h2" size="lg" centered className={styles.heading}>
        <FormattedMessage id="connection.onboarding.title" />
      </Heading>
      <div className={styles.connectors}>
        <div className={styles.sources}>
          <Text bold as="div" className={styles.sourcesTitle}>
            <Tooltip
              control={
                <>
                  <FormattedMessage id="connection.onboarding.sources" /> <FontAwesomeIcon icon={faCircleQuestion} />
                </>
              }
            >
              <FormattedMessage id="connection.onboarding.sourcesDescription" />
            </Tooltip>
          </Text>
          {sources.map((source, index) => {
            const tooltipText = formatMessage({ id: "connection.onboarding.addSource" }, { source: source?.name });
            return (
              <Tooltip
                placement="right"
                control={
                  <button
                    data-testid={`onboardingSource-${index}`}
                    data-sourceDefinitionId={source?.sourceDefinitionId}
                    aria-label={tooltipText}
                    className={styles.connectorButton}
                    onClick={() => onCreate(source?.sourceDefinitionId)}
                    onMouseEnter={() => setHighlightedSource(index as 0 | 1 | 2)}
                  >
                    <div className={styles.connectorIcon}>{getIcon(source?.icon)}</div>
                  </button>
                }
              >
                {tooltipText}
              </Tooltip>
            );
          })}

          <Tooltip
            placement="right"
            control={
              <button
                data-testid="onboardingSource-more"
                className={styles.connectorButton}
                onClick={() => onCreate()}
                onMouseEnter={() => setHighlightedSource(3)}
                aria-label={moreSourcesTooltip}
              >
                <PlusIcon className={styles.moreIcon} />
              </button>
            }
          >
            {moreSourcesTooltip}
          </Tooltip>
        </div>
        <div className={styles.airbyte} aria-hidden="true">
          <AirbyteIllustration sourceHighlighted={highlightedSource} destinationHighlighted={highlightedDestination} />
        </div>
        <div className={styles.destinations}>
          <Text bold as="div" className={styles.destinationsTitle}>
            <Tooltip
              control={
                <span>
                  <FormattedMessage id="connection.onboarding.destinations" />{" "}
                  <FontAwesomeIcon icon={faCircleQuestion} />
                </span>
              }
            >
              <FormattedMessage id="connection.onboarding.destinationsDescription" />
            </Tooltip>
          </Text>
          {destinations.map((destination, index) => {
            const tooltipText = formatMessage(
              { id: "connection.onboarding.addDestination" },
              { destination: destination?.name }
            );
            return (
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
                    aria-label={tooltipText}
                    tabIndex={-1}
                  >
                    <div className={styles.connectorIcon}>{getIcon(destination?.icon)}</div>
                  </button>
                }
              >
                {tooltipText}
              </Tooltip>
            );
          })}
          <Tooltip
            placement="right"
            control={
              <button
                className={styles.connectorButton}
                // onMouseEnter doesn't trigger on disabled buttons in React
                // https://github.com/facebook/react/issues/10109
                // Thus we just disable it via aria-disabled and make it non focusable via tabindex
                onMouseEnter={() => setHighlightedDestination(3)}
                aria-disabled="true"
                aria-label={moreDestinationsTooltip}
                tabIndex={-1}
              >
                <PlusIcon className={styles.moreIcon} />
              </button>
            }
          >
            {moreDestinationsTooltip}
          </Tooltip>
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
