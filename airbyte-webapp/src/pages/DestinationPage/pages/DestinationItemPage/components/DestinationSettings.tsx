import React from "react";
import { FormattedMessage } from "react-intl";

import DeleteBlock from "components/DeleteBlock";

import { ConnectionConfiguration } from "core/domain/connection";
import { Connector } from "core/domain/connector";
import { DestinationRead, WebBackendConnectionRead } from "core/request/AirbyteClient";
import { useFormChangeTrackerService, useUniqueFormId } from "hooks/services/FormChangeTracker";
import { useDeleteDestination, useUpdateDestination } from "hooks/services/useDestinationHook";
import { useDestinationDefinition } from "services/connector/DestinationDefinitionService";
import { useGetDestinationDefinitionSpecification } from "services/connector/DestinationDefinitionSpecificationService";
import { ConnectorCard } from "views/Connector/ConnectorCard";

import styles from "./DestinationSettings.module.scss";

interface DestinationsSettingsProps {
  currentDestination: DestinationRead;
  connectionsWithDestination: WebBackendConnectionRead[];
}

const DestinationsSettings: React.FC<DestinationsSettingsProps> = ({
  currentDestination,
  connectionsWithDestination,
}) => {
  const destinationSpecification = useGetDestinationDefinitionSpecification(currentDestination.destinationDefinitionId);
  const destinationDefinition = useDestinationDefinition(currentDestination.destinationDefinitionId);
  const { mutateAsync: updateDestination } = useUpdateDestination();
  const { mutateAsync: deleteDestination } = useDeleteDestination();
  const formId = useUniqueFormId();
  const { clearFormChange } = useFormChangeTrackerService();

  const onSubmitForm = async (values: {
    name: string;
    serviceType: string;
    connectionConfiguration?: ConnectionConfiguration;
  }) => {
    await updateDestination({
      values,
      destinationId: currentDestination.destinationId,
    });
  };

  const onDelete = async () => {
    clearFormChange(formId);
    await deleteDestination({
      connectionsWithDestination,
      destination: currentDestination,
    });
  };

  return (
    <div className={styles.content}>
      <ConnectorCard
        formId={formId}
        isEditMode
        onSubmit={onSubmitForm}
        formType="destination"
        availableServices={[destinationDefinition]}
        formValues={{
          ...currentDestination,
          serviceType: Connector.id(destinationDefinition),
        }}
        connector={currentDestination}
        selectedConnectorDefinitionSpecification={destinationSpecification}
        title={<FormattedMessage id="destination.destinationSettings" />}
      />
      <DeleteBlock type="destination" onDelete={onDelete} />
    </div>
  );
};

export default DestinationsSettings;
