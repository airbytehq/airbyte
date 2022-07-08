import React, { useEffect, useMemo, useState } from "react";

import { ContentCard } from "components";
import { SelectServiceType } from "components/SelectServiceType/SelectServiceType";

import { ConnectionConfiguration } from "core/domain/connection";
import { Connector } from "core/domain/connector";
import { JobInfo } from "core/domain/job";
import { useCreateDestination } from "hooks/services/useDestinationHook";
import { TrackActionType, useTrackAction } from "hooks/useTrackAction";
import { useDestinationDefinitionList } from "services/connector/DestinationDefinitionService";
import { useGetDestinationDefinitionSpecificationAsync } from "services/connector/DestinationDefinitionSpecificationService";
import { createFormErrorMessage } from "utils/errorStatusMessage";
import { ConnectorCard } from "views/Connector/ConnectorCard";
import { useDocumentationPanelContext } from "views/Connector/ConnectorDocumentationLayout/DocumentationPanelContext";

import styles from "./StepsCommonStyling.module.scss";

interface Props {
  onNextStep: () => void;
  onSuccess: () => void;
}

const DestinationStep: React.FC<Props> = ({ onNextStep, onSuccess }) => {
  const [destinationDefinitionId, setDestinationDefinitionId] = useState<string | null>(null);
  const { setDocumentationUrl, setDocumentationPanelOpen } = useDocumentationPanelContext();
  const { data: destinationDefinitionSpecification, isLoading } =
    useGetDestinationDefinitionSpecificationAsync(destinationDefinitionId);
  const { destinationDefinitions } = useDestinationDefinitionList();
  const [successRequest, setSuccessRequest] = useState(false);
  const [error, setError] = useState<{
    status: number;
    response: JobInfo;
    message: string;
  } | null>(null);

  const { mutateAsync: createDestination } = useCreateDestination();
  const trackNewDestinationAction = useTrackAction(TrackActionType.NEW_DESTINATION);

  const getDestinationDefinitionById = (id: string) =>
    destinationDefinitions.find((item) => item.destinationDefinitionId === id);

  useEffect(() => {
    return () => {
      setDocumentationPanelOpen(false);
    };
  }, [setDocumentationPanelOpen]);

  const onSubmitDestinationStep = async (values: {
    name: string;
    serviceType: string;
    destinationDefinitionId?: string;
    connectionConfiguration?: ConnectionConfiguration;
  }) => {
    setError(null);
    const destinationConnector = getDestinationDefinitionById(values.serviceType);

    try {
      await createDestination({
        values,
        destinationConnector,
      });

      setSuccessRequest(true);
      onSuccess();
      setTimeout(() => {
        setSuccessRequest(false);
        onNextStep();
      }, 2000);
    } catch (e) {
      setError(e);
    }
  };

  const onDropDownSelect = (destinationDefinitionId: string) => {
    setDocumentationPanelOpen(false);
    const destinationConnector = getDestinationDefinitionById(destinationDefinitionId);
    setDocumentationUrl(destinationConnector?.documentationUrl || "");

    trackNewDestinationAction("Select a connector", {
      connector_destination: destinationConnector?.name,
      connector_destination_definition_id: destinationConnector?.destinationDefinitionId,
    });

    setError(null);
    setDestinationDefinitionId(destinationDefinitionId);
  };
  const onSubmitForm = async (values: { name: string }) => {
    await onSubmitDestinationStep({
      ...values,
      serviceType: "asdfasdf",
      destinationDefinitionId: destinationDefinitionSpecification?.destinationDefinitionId,
    });
  };

  const errorMessage = error ? createFormErrorMessage(error) : null;

  const selectedService = useMemo(
    () => destinationDefinitions.find((s) => Connector.id(s) === destinationDefinitionId),
    [destinationDefinitions, destinationDefinitionId]
  );

  return (
    <>
      <ContentCard className={styles.contentCard}>
        <SelectServiceType
          formType="destination"
          value={destinationDefinitionId}
          onChangeServiceType={onDropDownSelect}
          availableServices={destinationDefinitions}
        />
      </ContentCard>
      {selectedService && (
        <ConnectorCard
          full
          formType="destination"
          onSubmit={onSubmitForm}
          hasSuccess={successRequest}
          errorMessage={errorMessage}
          selectedConnectorDefinitionSpecification={destinationDefinitionSpecification}
          isLoading={isLoading}
          selectedService={selectedService}
        />
      )}
    </>
  );
};

export default DestinationStep;
