import React from "react";
import { FormattedMessage } from "react-intl";

import { DeleteBlock } from "components/common/DeleteBlock";

import { DestinationRead, WebBackendConnectionListItem } from "core/request/AirbyteClient";
import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { useFormChangeTrackerService, useUniqueFormId } from "hooks/services/FormChangeTracker";
import { useDeleteDestination, useUpdateDestination } from "hooks/services/useDestinationHook";
import { useDestinationDefinition } from "services/connector/DestinationDefinitionService";
import { useGetDestinationDefinitionSpecification } from "services/connector/DestinationDefinitionSpecificationService";
import { ConnectorCard } from "views/Connector/ConnectorCard";
import { ConnectorCardValues } from "views/Connector/ConnectorForm";

import styles from "./DestinationSettings.module.scss";

interface DestinationsSettingsProps {
  currentDestination: DestinationRead;
  connectionsWithDestination: WebBackendConnectionListItem[];
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

  useTrackPage(PageTrackingCodes.DESTINATION_ITEM_SETTINGS);

  const onSubmitForm = async (values: ConnectorCardValues) => {
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
        formType="destination"
        title={<FormattedMessage id="destination.destinationSettings" />}
        isEditMode
        formId={formId}
        availableConnectorDefinitions={[destinationDefinition]}
        selectedConnectorDefinitionSpecification={destinationSpecification}
        connector={currentDestination}
        onSubmit={onSubmitForm}
      />
      <DeleteBlock type="destination" onDelete={onDelete} />
    </div>
  );
};

export default DestinationsSettings;
