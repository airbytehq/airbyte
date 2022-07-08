import React, { useMemo, useState } from "react";
import { FormattedMessage } from "react-intl";

import { ContentCard } from "components";
import { SelectServiceType } from "components/SelectServiceType/SelectServiceType";
import TitleBlock from "components/TitleBlock/TitleBlock";

import { ConnectionConfiguration } from "core/domain/connection";
import { Connector } from "core/domain/connector";
import { DestinationDefinitionRead } from "core/request/AirbyteClient";
import { LogsRequestError } from "core/request/LogsRequestError";
import useRouter from "hooks/useRouter";
import { TrackActionType, useTrackAction } from "hooks/useTrackAction";
import { useGetDestinationDefinitionSpecificationAsync } from "services/connector/DestinationDefinitionSpecificationService";
import { createFormErrorMessage } from "utils/errorStatusMessage";
import { ConnectorCard } from "views/Connector/ConnectorCard";

import styles from "./DestinationForm.module.scss";

interface DestinationFormProps {
  onSubmit: (values: {
    name: string;
    serviceType: string;
    destinationDefinitionId?: string;
    connectionConfiguration?: ConnectionConfiguration;
  }) => void;
  afterSelectConnector?: () => void;
  destinationDefinitions: DestinationDefinitionRead[];
  hasSuccess?: boolean;
  error?: { message?: string; status?: number } | null;
}

const hasDestinationDefinitionId = (state: unknown): state is { destinationDefinitionId: string } => {
  return (
    typeof state === "object" &&
    state !== null &&
    typeof (state as { destinationDefinitionId?: string }).destinationDefinitionId === "string"
  );
};

export const DestinationForm: React.FC<DestinationFormProps> = ({
  onSubmit,
  destinationDefinitions,
  error,
  hasSuccess,
  afterSelectConnector,
}) => {
  const { location } = useRouter();
  const trackNewDestinationAction = useTrackAction(TrackActionType.NEW_DESTINATION);

  const [destinationDefinitionId, setDestinationDefinitionId] = useState(
    hasDestinationDefinitionId(location.state) ? location.state.destinationDefinitionId : null
  );

  const {
    data: destinationDefinitionSpecification,
    error: destinationDefinitionError,
    isLoading,
  } = useGetDestinationDefinitionSpecificationAsync(destinationDefinitionId);

  const onDropDownSelect = (destinationDefinitionId: string) => {
    setDestinationDefinitionId(destinationDefinitionId);

    const connector = destinationDefinitions.find((item) => item.destinationDefinitionId === destinationDefinitionId);

    if (afterSelectConnector) {
      afterSelectConnector();
    }

    trackNewDestinationAction("Select a connector", {
      connector_destination: connector?.name,
      connector_destination_definition_id: destinationDefinitionId,
    });
  };

  const onSubmitForm = async (values: { name: string }) => {
    await onSubmit({
      ...values,
      serviceType: destinationDefinitionId as string,
      destinationDefinitionId: destinationDefinitionSpecification?.destinationDefinitionId,
    });
  };

  const selectedService = useMemo(
    () => destinationDefinitions.find((s) => Connector.id(s) === destinationDefinitionId),
    [destinationDefinitions, destinationDefinitionId]
  );

  const errorMessage = error ? createFormErrorMessage(error) : null;

  return (
    <div>
      <ContentCard className={styles.contentCard}>
        <TitleBlock title={<FormattedMessage id="onboarding.destinationSetUp" />} />
        <div className={styles.serviceTypeContainer}>
          <SelectServiceType
            formType="destination"
            value={destinationDefinitionId}
            onChangeServiceType={onDropDownSelect}
            availableServices={destinationDefinitions}
          />
        </div>
      </ContentCard>
      {selectedService && (
        <ConnectorCard
          fetchingConnectorError={destinationDefinitionError instanceof Error ? destinationDefinitionError : null}
          onSubmit={onSubmitForm}
          formType="destination"
          selectedConnectorDefinitionSpecification={destinationDefinitionSpecification}
          hasSuccess={hasSuccess}
          errorMessage={errorMessage}
          isLoading={isLoading}
          selectedService={selectedService}
          formValues={{ name: selectedService.name }}
          jobInfo={LogsRequestError.extractJobInfo(error)}
        />
      )}
    </div>
  );
};
