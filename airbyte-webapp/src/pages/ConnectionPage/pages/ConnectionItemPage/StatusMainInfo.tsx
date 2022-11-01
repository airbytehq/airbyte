import { faArrowRight } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import React from "react";
import { FormattedMessage } from "react-intl";
import { Link } from "react-router-dom";

import { ConnectorCard } from "components";
import { Button } from "components/ui/Button";
import { Text } from "components/ui/Text";

import { ConnectionStatus, SchemaChange } from "core/request/AirbyteClient";
import { useConnectionEditService } from "hooks/services/ConnectionEdit/ConnectionEditService";
import { FeatureItem, useFeature } from "hooks/services/Feature";
import { RoutePaths } from "pages/routePaths";
import { useDestinationDefinition } from "services/connector/DestinationDefinitionService";
import { useSourceDefinition } from "services/connector/SourceDefinitionService";
import { useRefreshSourceSchemaWithConfirmationOnDirty } from "views/Connection/ConnectionForm/components/refreshSourceSchemaWithConfirmationOnDirty";

import EnabledControl from "./EnabledControl";
import styles from "./StatusMainInfo.module.scss";

export const StatusMainInfo: React.FC = () => {
  const isSchemaChangesFeatureEnabled = process.env.REACT_APP_AUTO_DETECT_SCHEMA_CHANGES === "true" ?? false;

  const {
    connection: { source, destination, status, schemaChange },
  } = useConnectionEditService();
  const sourceDefinition = useSourceDefinition(source.sourceDefinitionId);
  const destinationDefinition = useDestinationDefinition(destination.destinationDefinitionId);

  const hasAllowSyncFeature = useFeature(FeatureItem.AllowSync);
  const refreshSchema = useRefreshSourceSchemaWithConfirmationOnDirty(false);

  const sourceConnectionPath = `../../${RoutePaths.Source}/${source.sourceId}`;
  const destinationConnectionPath = `../../${RoutePaths.Destination}/${destination.destinationId}`;

  const hasSchemaChanges = isSchemaChangesFeatureEnabled && schemaChange !== SchemaChange.no_change;
  const hasBreakingSchemaChange = hasSchemaChanges && schemaChange === SchemaChange.breaking;
  const hasNonBreakingSchemaChange = hasSchemaChanges && schemaChange === SchemaChange.non_breaking;
  const schemaChangeClassNames = {
    [styles.breaking]: hasBreakingSchemaChange,
    [styles.nonBreaking]: hasNonBreakingSchemaChange,
  };

  return (
    <div className={styles.container}>
      <div className={styles.pathContainer}>
        <Link to={sourceConnectionPath} className={classNames(styles.connectorLink, schemaChangeClassNames)}>
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
          <EnabledControl disabled={!hasAllowSyncFeature || hasBreakingSchemaChange} />
        </div>
      )}
      {hasSchemaChanges && (
        <div className={classNames(styles.schemaChanges, schemaChangeClassNames)}>
          <Text size="lg">
            <FormattedMessage
              id={`connection.schemaChange.${schemaChange === SchemaChange.breaking ? "breaking" : "nonBreaking"}`}
            />
          </Text>
          <Button onClick={() => refreshSchema()}>
            <FormattedMessage id="connection.schemaChange.reviewCTA" />
          </Button>
        </div>
      )}
    </div>
  );
};
