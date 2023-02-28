import React, { useEffect } from "react";
import { FormattedMessage } from "react-intl";

import { ConnectionConfiguration } from "core/domain/connection";
import { DestinationRead } from "core/request/AirbyteClient";
import { DestinationCloneRequestBody } from "core/request/AirbyteClient";
import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { useUniqueFormId } from "hooks/services/FormChangeTracker"; // useFormChangeTrackerService
import { useCloneDestination } from "hooks/services/useDestinationHook";
import useRouter from "hooks/useRouter";
import { useDestinationDefinition } from "services/connector/DestinationDefinitionService";
import { useGetDestinationDefinitionSpecification } from "services/connector/DestinationDefinitionSpecificationService";
import { ConnectorCard } from "views/Connector/ConnectorCard";
import { useDocumentationPanelContext } from "views/Connector/ConnectorDocumentationLayout/DocumentationPanelContext";
import { ServiceFormValues } from "views/Connector/ServiceForm";

import styles from "./DestinationCopy.module.scss";

interface DestinationSettingsProps {
  currentDestination: DestinationRead;
  errorMessage?: JSX.Element | string | null;
  onBack?: () => void;
  formValues?: ServiceFormValues | null;
  afterSubmit?: () => void;
  onShowLoading?: (
    isLoading: boolean,
    formValues: ServiceFormValues | null,
    error: JSX.Element | string | null
  ) => void;
}

const DestinationCopy: React.FC<DestinationSettingsProps> = ({
  currentDestination,
  errorMessage,
  formValues,
  onBack,
  onShowLoading,
  afterSubmit,
}) => {
  const { mutateAsync: cloneDestination } = useCloneDestination();
  const { setDocumentationPanelOpen } = useDocumentationPanelContext();
  const formId = useUniqueFormId();
  const { query } = useRouter<{ id: string }, { id: string; "*": string }>();
  // const { clearFormChange } = useFormChangeTrackerService();

  useTrackPage(PageTrackingCodes.SOURCE_ITEM_SETTINGS);
  useEffect(() => {
    return () => {
      setDocumentationPanelOpen(false);
    };
  }, [setDocumentationPanelOpen]);

  const destinationDefinitionSpecification = useGetDestinationDefinitionSpecification(
    currentDestination.destinationDefinitionId
  );

  const destinationDefinition = useDestinationDefinition(currentDestination.destinationDefinitionId);

  const onSubmit = async (values: {
    name: string;
    serviceType: string;
    connectionConfiguration?: ConnectionConfiguration;
  }) => {
    const cloneDestinationData: DestinationCloneRequestBody = {
      destinationCloneId: query.id,
      destinationConfiguration: {
        name: values.name,
        connectionConfiguration: values.connectionConfiguration,
      },
    };
    await cloneDestination({ destination: cloneDestinationData });
    if (afterSubmit) {
      afterSubmit();
    }
  };

  const defaultFormValues = formValues?.serviceType
    ? formValues
    : {
        ...currentDestination,
        serviceType: currentDestination.destinationDefinitionId,
        name: `${currentDestination.name} (Copy)`,
      };

  return (
    <div className={styles.content}>
      <ConnectorCard
        formId={formId}
        title={<FormattedMessage id="destination.destinationSettings" />}
        onSubmit={onSubmit}
        isCopyMode
        formType="destination"
        connector={currentDestination}
        availableServices={[destinationDefinition]}
        formValues={defaultFormValues}
        selectedConnectorDefinitionSpecification={destinationDefinitionSpecification}
        onBack={onBack}
        onShowLoading={onShowLoading}
        errorMessage={errorMessage}
      />
    </div>
  );
};

export default DestinationCopy;
