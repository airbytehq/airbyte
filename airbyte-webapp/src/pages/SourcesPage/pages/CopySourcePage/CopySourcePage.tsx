import React, { useState } from "react"; // useMemo
import styled from "styled-components";

// import { useConnectionList } from "hooks/services/useConnectionHook";
import { ConnectionStep, CreateStepTypes } from "components/ConnectionStep";

import { useGetSource } from "hooks/services/useSourceHook";
import useRouter from "hooks/useRouter";
// import { useSourceDefinition } from "services/connector/SourceDefinitionService";
import { ConnectorDocumentationWrapper } from "views/Connector/ConnectorDocumentationLayout";
import { ServiceFormValues } from "views/Connector/ServiceForm/types";
import TestConnection from "views/Connector/TestConnection";

import { RoutePaths } from "../../../routePaths";
import SourceCopy from "./components/SourceCopy";

const Container = styled.div`
  padding: 0px 0px 0px 70px;
`;

const CopySourcePage: React.FC = () => {
  const { query, push } = useRouter<{ id: string }, { id: string; "*": string }>();
  const [currentStep, setCurrentStep] = useState(CreateStepTypes.CREATE_SOURCE);
  const [loadingStatus, setLoadingStatus] = useState<boolean>(true);
  const [fetchingConnectorError, setFetchingConnectorError] = useState<JSX.Element | string | null>(null);
  const [sourceFormValues, setSourceFormValues] = useState<ServiceFormValues | null>({
    name: "",
    serviceType: "",
    connectionConfiguration: {},
  });

  const source = useGetSource(query.id);
  //   const sourceDefinition = useSourceDefinition(source?.sourceDefinitionId);

  const goBack = () => {
    push(`/${RoutePaths.Source}`);
  };

  return (
    <>
      <ConnectionStep lightMode type="source" activeStep={CreateStepTypes.CREATE_SOURCE} />
      <ConnectorDocumentationWrapper>
        <Container>
          {currentStep === CreateStepTypes.TEST_CONNECTION && (
            <TestConnection
              isLoading={loadingStatus}
              type="source"
              onBack={() => {
                setCurrentStep(CreateStepTypes.CREATE_SOURCE);
              }}
              onFinish={() => {
                goBack();
              }}
            />
          )}
          {currentStep === CreateStepTypes.CREATE_SOURCE && (
            <SourceCopy
              currentSource={source}
              errorMessage={fetchingConnectorError}
              onBack={goBack}
              formValues={sourceFormValues}
              afterSubmit={() => {
                setLoadingStatus(false);
              }}
              onShowLoading={(
                isLoading: boolean,
                formValues: ServiceFormValues | null,
                error: JSX.Element | string | null
              ) => {
                setSourceFormValues(formValues);
                if (isLoading) {
                  setCurrentStep(CreateStepTypes.TEST_CONNECTION);
                  setLoadingStatus(true);
                } else {
                  setCurrentStep(CreateStepTypes.CREATE_SOURCE);
                  setFetchingConnectorError(error || null);
                }
              }}
            />
          )}
        </Container>
      </ConnectorDocumentationWrapper>
    </>
  );
};

export default CopySourcePage;
