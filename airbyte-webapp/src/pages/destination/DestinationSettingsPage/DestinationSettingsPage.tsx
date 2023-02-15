import React, { useCallback, useMemo } from "react";
import { FormattedMessage } from "react-intl";
import { useOutletContext } from "react-router-dom";

import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { useFormChangeTrackerService, useUniqueFormId } from "hooks/services/FormChangeTracker";
import { useConnectionList } from "hooks/services/useConnectionHook";
import {
  useDeleteDestination,
  useInvalidateDestination,
  useUpdateDestination,
} from "hooks/services/useDestinationHook";
import { useDeleteModal } from "hooks/useDeleteModal";
import { useDestinationDefinition } from "services/connector/DestinationDefinitionService";
import { useGetDestinationDefinitionSpecification } from "services/connector/DestinationDefinitionSpecificationService";
import { ConnectorCard } from "views/Connector/ConnectorCard";
import { ConnectorCardValues } from "views/Connector/ConnectorForm/types";

import styles from "./DestinationSettings.module.scss";
import { DestinationOutletContext } from "../types";

export const DestinationSettingsPage: React.FC = () => {
  const { destination } = useOutletContext<DestinationOutletContext>();
  const { connections: connectionsWithDestination } = useConnectionList({ destinationId: [destination.destinationId] });
  const destinationSpecification = useGetDestinationDefinitionSpecification(destination.destinationDefinitionId);
  const destinationDefinition = useDestinationDefinition(destination.destinationDefinitionId);
  const reloadDestination = useInvalidateDestination(destination.destinationId);
  const { mutateAsync: updateDestination } = useUpdateDestination();
  const { mutateAsync: deleteDestination } = useDeleteDestination();
  const formId = useUniqueFormId();
  const { clearFormChange } = useFormChangeTrackerService();

  useTrackPage(PageTrackingCodes.DESTINATION_ITEM_SETTINGS);

  const onSubmitForm = async (values: ConnectorCardValues) => {
    await updateDestination({
      values,
      destinationId: destination.destinationId,
    });
  };

  const onDelete = useCallback(async () => {
    clearFormChange(formId);
    await deleteDestination({
      connectionsWithDestination,
      destination,
    });
  }, [clearFormChange, connectionsWithDestination, deleteDestination, destination, formId]);

  const modalAdditionalContent = useMemo<React.ReactNode>(() => {
    if (connectionsWithDestination.length === 0) {
      return null;
    }
    return (
      <p>
        <FormattedMessage
          id="tables.affectedConnectionsOnDeletion"
          values={{ count: connectionsWithDestination.length }}
        />
        {connectionsWithDestination.map((connection) => (
          <React.Fragment key={connection.connectionId}>
            - <strong>{`${connection.name}\n`}</strong>
          </React.Fragment>
        ))}
      </p>
    );
  }, [connectionsWithDestination]);

  const onDeleteClick = useDeleteModal("destination", onDelete, modalAdditionalContent);

  return (
    <div className={styles.content}>
      <ConnectorCard
        formType="destination"
        title={<FormattedMessage id="destination.destinationSettings" />}
        isEditMode
        formId={formId}
        availableConnectorDefinitions={[destinationDefinition]}
        selectedConnectorDefinitionSpecification={destinationSpecification}
        selectedConnectorDefinitionId={destinationSpecification.destinationDefinitionId}
        connector={destination}
        reloadConfig={reloadDestination}
        onSubmit={onSubmitForm}
        onDeleteClick={onDeleteClick}
      />
    </div>
  );
};
