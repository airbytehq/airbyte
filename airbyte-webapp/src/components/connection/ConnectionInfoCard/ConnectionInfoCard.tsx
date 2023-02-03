import { faArrowRight } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import React from "react";
import { Link } from "react-router-dom";

import { ConnectorCard } from "components";

import { ConnectionStatus } from "core/request/AirbyteClient";
import { useSchemaChanges } from "hooks/connection/useSchemaChanges";
import { useConnectionEditService } from "hooks/services/ConnectionEdit/ConnectionEditService";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";
import { FeatureItem, useFeature } from "hooks/services/Feature";
import { RoutePaths } from "pages/routePaths";

import styles from "./ConnectionInfoCard.module.scss";
import { EnabledControl } from "./EnabledControl";
import { SchemaChangesDetected } from "./SchemaChangesDetected";

export const ConnectionInfoCard: React.FC = () => {
  const {
    connection: { source, destination, status, schemaChange },
    schemaHasBeenRefreshed,
  } = useConnectionEditService();
  const { hasSchemaChanges, hasBreakingSchemaChange, hasNonBreakingSchemaChange } = useSchemaChanges(schemaChange);
  const { sourceDefinition, destDefinition } = useConnectionFormService();

  const hasAllowSyncFeature = useFeature(FeatureItem.AllowSync);

  const sourceConnectionPath = `../../${RoutePaths.Source}/${source.sourceId}`;
  const destinationConnectionPath = `../../${RoutePaths.Destination}/${destination.destinationId}`;

  const isConnectionReadOnly = status === ConnectionStatus.deprecated;

  const schemaChangeClassNames =
    isConnectionReadOnly || schemaHasBeenRefreshed
      ? undefined
      : {
          [styles.breaking]: hasBreakingSchemaChange,
          [styles.nonBreaking]: hasNonBreakingSchemaChange,
        };

  return (
    <div className={styles.container} data-testid="connectionInfo">
      <div className={styles.pathContainer}>
        <Link
          to={sourceConnectionPath}
          className={classNames(styles.connectorLink, schemaChangeClassNames)}
          data-testid="connectionInfo-sourceLink"
        >
          <ConnectorCard
            connectionName={source.sourceName}
            icon={source?.icon}
            connectorName={source.name}
            releaseStage={sourceDefinition?.releaseStage}
          />
        </Link>
        <FontAwesomeIcon icon={faArrowRight} />
        <Link
          to={destinationConnectionPath}
          className={styles.connectorLink}
          data-testid="connectionInfo-destinationLink"
        >
          <ConnectorCard
            connectionName={destination.destinationName}
            icon={destination?.icon}
            connectorName={destination.name}
            releaseStage={destDefinition?.releaseStage}
          />
        </Link>
      </div>
      {!isConnectionReadOnly && (
        <>
          <div className={styles.enabledControlContainer}>
            <EnabledControl disabled={!hasAllowSyncFeature || hasBreakingSchemaChange} />
          </div>
          {hasSchemaChanges && <SchemaChangesDetected />}
        </>
      )}
    </div>
  );
};
