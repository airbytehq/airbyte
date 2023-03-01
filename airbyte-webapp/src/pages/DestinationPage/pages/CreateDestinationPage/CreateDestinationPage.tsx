import React, { useState } from "react";

import { ConnectionStep, CreateStepTypes } from "components/ConnectionStep";
import { FormPageContent } from "components/ConnectorBlocks";

import { ConnectionConfiguration } from "core/domain/connection";
import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { useCreateDestination } from "hooks/services/useDestinationHook";
import useRouter from "hooks/useRouter";
import { RoutePaths } from "pages/routePaths";
import { useDestinationDefinitionList } from "services/connector/DestinationDefinitionService";
import { ConnectorDocumentationWrapper } from "views/Connector/ConnectorDocumentationLayout";
import { ServiceFormValues } from "views/Connector/ServiceForm/types";
import TestConnection from "views/Connector/TestConnection/TestConnection";

import { DestinationForm } from "./components/DestinationForm";

export const CreateDestinationPage: React.FC = () => {
  useTrackPage(PageTrackingCodes.DESTINATION_NEW);

  const { push, location } = useRouter();
  const [successRequest, setSuccessRequest] = useState(false);
  const { destinationDefinitions } = useDestinationDefinitionList();
  const { mutateAsync: createDestination } = useCreateDestination();

  const [currentStep, setCurrentStep] = useState<string>(CreateStepTypes.CREATE_DESTINATION);
  const [isLoading, setLoadingStatus] = useState<boolean>(true);
  const [fetchingConnectorError, setFetchingConnectorError] = useState<JSX.Element | string | null>(null);
  const [formValues, setFormValues] = useState<ServiceFormValues>({
    name: "",
    serviceType: "",
    connectionConfiguration: {},
  });

  const onSubmitDestinationForm = async (values: {
    name: string;
    serviceType: string;
    connectionConfiguration?: ConnectionConfiguration;
  }) => {
    const connector = destinationDefinitions.find((item) => item.destinationDefinitionId === values.serviceType);
    await createDestination({
      values,
      destinationConnector: connector,
    });
    setSuccessRequest(true);
    setLoadingStatus(false);
    setTimeout(() => {
      setSuccessRequest(false);
      //  push(`../${result.destinationId}`);
    }, 2000);
  };

  const handleBackButton = () => {
    if (currentStep === CreateStepTypes.TEST_CONNECTION) {
      setCurrentStep(CreateStepTypes.CREATE_DESTINATION);
      return;
    }
    push(`/${RoutePaths.Destination}/${RoutePaths.SelectDestination}`, {
      state: {
        ...(location.state as Record<string, unknown>),
      },
    });
  };

  const handleFinishButton = () => {
    push(`/${RoutePaths.Destination}`);
  };

  const onShowLoading = (isLoading: boolean, formValues: ServiceFormValues, error: JSX.Element | string | null) => {
    if (isLoading) {
      setCurrentStep(CreateStepTypes.TEST_CONNECTION);
    } else {
      setCurrentStep(CreateStepTypes.CREATE_DESTINATION);
    }
    setFormValues(formValues);
    setLoadingStatus(isLoading || false);
    setFetchingConnectorError(error || null);
  };

  return (
    <>
      <ConnectionStep lightMode type="destination" activeStep={CreateStepTypes.CREATE_SOURCE} />
      <ConnectorDocumentationWrapper>
        <FormPageContent>
          {currentStep === CreateStepTypes.TEST_CONNECTION && (
            <TestConnection
              onBack={handleBackButton}
              onFinish={handleFinishButton}
              isLoading={isLoading}
              type="destination"
            />
          )}
          {currentStep === CreateStepTypes.CREATE_DESTINATION && (
            <DestinationForm
              onSubmit={onSubmitDestinationForm}
              destinationDefinitions={destinationDefinitions}
              hasSuccess={successRequest}
              onShowLoading={onShowLoading}
              onBack={handleBackButton}
              error={fetchingConnectorError}
              formValues={formValues}
            />
          )}
        </FormPageContent>
      </ConnectorDocumentationWrapper>
    </>
  );
};
