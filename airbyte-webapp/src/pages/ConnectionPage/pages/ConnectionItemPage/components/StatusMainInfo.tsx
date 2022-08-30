import { faArrowRight } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import { Link } from "react-router-dom";

import ConnectorCard from "components/ConnectorCard";

import { getFrequencyType } from "config/utils";
import { ConnectionStatus, SourceRead, DestinationRead, WebBackendConnectionRead } from "core/request/AirbyteClient";
import { FeatureItem, useFeature } from "hooks/services/Feature";
import { RoutePaths } from "pages/routePaths";
import { useDestinationDefinition } from "services/connector/DestinationDefinitionService";
import { useSourceDefinition } from "services/connector/SourceDefinitionService";

import EnabledControl from "./EnabledControl";
import styles from "./StatusMainInfo.module.scss";

interface StatusMainInfoProps {
  connection: WebBackendConnectionRead;
  source: SourceRead;
  destination: DestinationRead;
  onStatusUpdating?: (updating: boolean) => void;
}

export const StatusMainInfo: React.FC<StatusMainInfoProps> = ({
  onStatusUpdating,
  connection,
  source,
  destination,
}) => {
  const sourceDefinition = useSourceDefinition(source.sourceDefinitionId);
  const destinationDefinition = useDestinationDefinition(destination.destinationDefinitionId);

  const allowSync = useFeature(FeatureItem.AllowSync);

  const sourceConnectionPath = `../../${RoutePaths.Source}/${source.sourceId}`;
  const destinationConnectionPath = `../../${RoutePaths.Destination}/${destination.destinationId}`;

  return (
    <div className={styles.container}>
      <div className={styles.pathContainer}>
        <Link to={sourceConnectionPath} className={styles.connectorLink}>
          <ConnectorCard
            connectionName={source.sourceName}
            icon={sourceDefinition?.icon}
            connectorName={source.name}
            releaseStage={sourceDefinition?.releaseStage}
          />
        </Link>
        <FontAwesomeIcon icon={faArrowRight} />
        <Link to={destinationConnectionPath} className={styles.connectorLink}>
          <ConnectorCard
            connectionName={destination.destinationName}
            icon={destinationDefinition?.icon}
            connectorName={destination.name}
            releaseStage={destinationDefinition?.releaseStage}
          />
        </Link>
      </div>
      {connection.status !== ConnectionStatus.deprecated && (
        <div className={styles.enabledControlContainer}>
          <EnabledControl
            onStatusUpdating={onStatusUpdating}
            disabled={!allowSync}
            connection={connection}
            frequencyType={getFrequencyType(connection.scheduleData?.basicSchedule)}
          />
        </div>
      )}
    </div>
  );
};
