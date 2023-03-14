import React, { useState } from "react";

import { ConnectionStep, CreateStepTypes } from "components/ConnectionStep";
import { FormPageContent } from "components/ConnectorBlocks";
import HeadTitle from "components/HeadTitle";

import { ConnectionConfiguration } from "core/domain/connection";
import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { useCreateSource } from "hooks/services/useSourceHook";
import useRouter from "hooks/useRouter";
import { RoutePaths } from "pages/routePaths";
import { useSourceDefinitionList } from "services/connector/SourceDefinitionService";
import { ConnectorDocumentationWrapper } from "views/Connector/ConnectorDocumentationLayout/ConnectorDocumentationWrapper";
import { ServiceFormValues } from "views/Connector/ServiceForm/types";
import TestConnection from "views/Connector/TestConnection/TestConnection";

import { SourceForm } from "./components/SourceForm";

const CreateSourcePage: React.FC = () => {
  useTrackPage(PageTrackingCodes.SOURCE_NEW);
  const { push, location } = useRouter();
  const [successRequest, setSuccessRequest] = useState(false);
  const [currentStep, setCurrentStep] = useState<string>(CreateStepTypes.CREATE_SOURCE);
  const [isLoading, setLoadingStatus] = useState<boolean>(true);
  const [fetchingConnectorError, setFetchingConnectorError] = useState<JSX.Element | string | null>(null);
  const [formValues, setFormValues] = useState<ServiceFormValues>({
    name: "",
    serviceType: "",
    connectionConfiguration: {},
  });

  const { sourceDefinitions } = useSourceDefinitionList();
  const { mutateAsync: createSource } = useCreateSource();

  const onSubmitSourceStep = async (values: {
    name: string;
    serviceType: string;
    connectionConfiguration?: ConnectionConfiguration;
  }) => {
    const connector = sourceDefinitions.find((item) => item.sourceDefinitionId === values.serviceType);
    if (!connector) {
      // Unsure if this can happen, but the types want it defined
      throw new Error("No Connector Found");
    }
    await createSource({ values, sourceConnector: connector });
    setSuccessRequest(true);
    setLoadingStatus(false);

    setTimeout(() => {
      setSuccessRequest(false);
    }, 2000);
  };

  const handleBackButton = () => {
    if (currentStep === CreateStepTypes.TEST_CONNECTION) {
      setCurrentStep(CreateStepTypes.CREATE_SOURCE);
      return;
    }
    push(`/${RoutePaths.Source}/${RoutePaths.SelectSource}`, {
      state: {
        ...(location.state as Record<string, unknown>),
      },
    });
  };

  const handleFinishButton = () => {
    push(`/${RoutePaths.Source}`);
  };

  const onShowLoading = (isLoading: boolean, formValues: ServiceFormValues, error: JSX.Element | string | null) => {
    if (isLoading) {
      setCurrentStep(CreateStepTypes.TEST_CONNECTION);
    } else {
      setCurrentStep(CreateStepTypes.CREATE_SOURCE);
    }
    setFormValues(formValues);
    setLoadingStatus(isLoading || false);
    setFetchingConnectorError(error);
  };

  return (
    <>
      <HeadTitle titles={[{ id: "sources.newSourceTitle" }]} />
      <ConnectionStep lightMode type="source" />
      <ConnectorDocumentationWrapper>
        {currentStep === CreateStepTypes.TEST_CONNECTION && (
          <>
            {" "}
            <TestConnection
              onBack={handleBackButton}
              onFinish={handleFinishButton}
              isLoading={isLoading}
              type="source"
            />
          </>
        )}
        {currentStep === CreateStepTypes.CREATE_SOURCE && (
          <FormPageContent>
            <SourceForm
              onSubmit={onSubmitSourceStep}
              sourceDefinitions={sourceDefinitions}
              hasSuccess={successRequest}
              onShowLoading={onShowLoading}
              error={fetchingConnectorError}
              onBack={handleBackButton}
              formValues={formValues}
            />
          </FormPageContent>
        )}
      </ConnectorDocumentationWrapper>
    </>
  );
};

export default CreateSourcePage;
