import { faArrowRight } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import { Link } from "react-router-dom";

import { ConnectorCard } from "components";

import { ConnectionStatus } from "core/request/AirbyteClient";
import { useConnectionEditService } from "hooks/services/ConnectionEdit/ConnectionEditService";
import { FeatureItem, useFeature } from "hooks/services/Feature";
import { RoutePaths } from "pages/routePaths";
import { useDestinationDefinition } from "services/connector/DestinationDefinitionService";
import { useSourceDefinition } from "services/connector/SourceDefinitionService";

import EnabledControl from "./EnabledControl";
import styles from "./StatusMainInfo.module.scss";

export const StatusMainInfo: React.FC = () => {
  const {
    connection: { source, destination, status },
  } = useConnectionEditService();
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
      {status !== ConnectionStatus.deprecated && (
        <div className={styles.enabledControlContainer}>
          <EnabledControl disabled={!allowSync} />
        </div>
      )}
    </div>
  );
};
