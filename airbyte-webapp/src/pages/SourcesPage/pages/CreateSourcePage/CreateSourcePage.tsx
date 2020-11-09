import React, { useMemo, useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { useResource } from "rest-hooks";

import PageTitle from "../../../../components/PageTitle";
import StepsMenu from "../../../../components/StepsMenu";
import SourceStep from "./components/SourceStep";
import ConnectionStep from "./components/ConnectionStep";
import { Routes } from "../../../routes";
import useRouter from "../../../../components/hooks/useRouterHook";
import DestinationResource from "../../../../core/resources/Destination";
import config from "../../../../config";
import SourceDefinitionResource from "../../../../core/resources/SourceDefinition";
import DestinationDefinitionResource from "../../../../core/resources/DestinationDefinition";
import { Source } from "../../../../core/resources/Source";
import { SyncSchema } from "../../../../core/resources/Schema";
import useSource from "../../../../components/hooks/services/useSourceHook";
import useConnection from "../../../../components/hooks/services/useConnectionHook";

const Content = styled.div`
  max-width: 638px;
  margin: 13px auto;
`;

export enum StepsTypes {
  CREATE_SOURCE = "select-source",
  SET_UP_CONNECTION = "set-up-connection"
}

const CreateSourcePage: React.FC = () => {
  const { push } = useRouter();
  const [successRequest, setSuccessRequest] = useState(false);
  const [errorStatusRequest, setErrorStatusRequest] = useState<number>(0);

  const { destinations } = useResource(DestinationResource.listShape(), {
    workspaceId: config.ui.workspaceId
  });
  const currentDestination = destinations[0]; // Now we have only one destination. If we support multiple destinations we will fix this line
  const { sourceDefinitions } = useResource(
    SourceDefinitionResource.listShape(),
    {
      workspaceId: config.ui.workspaceId
    }
  );
  const destinationDefinition = useResource(
    DestinationDefinitionResource.detailShape(),
    {
      destinationDefinitionId: currentDestination.destinationDefinitionId
    }
  );
  const { createSource } = useSource();
  const { createConnection } = useConnection();

  const [currentStep, setCurrentStep] = useState(StepsTypes.CREATE_SOURCE);

  const sourcesDropDownData = useMemo(
    () =>
      sourceDefinitions.map(item => ({
        text: item.name,
        value: item.sourceDefinitionId,
        img: "/default-logo-catalog.svg"
      })),
    [sourceDefinitions]
  );

  const [currentsource, setCurrentsource] = useState<Source | undefined>(
    undefined
  );

  const onSubmitSourceStep = async (values: {
    name: string;
    serviceType: string;
    connectionConfiguration?: any;
  }) => {
    const connector = sourceDefinitions.find(
      item => item.sourceDefinitionId === values.serviceType
    );
    setErrorStatusRequest(0);
    try {
      const result = await createSource({ values, sourceConnector: connector });
      setCurrentsource(result);
      setSuccessRequest(true);
      setTimeout(() => {
        setSuccessRequest(false);
        setCurrentStep(StepsTypes.SET_UP_CONNECTION);
      }, 2000);
    } catch (e) {
      setErrorStatusRequest(e.status);
    }
  };

  const onSubmitConnectionStep = async (values: {
    frequency: string;
    syncSchema: SyncSchema;
  }) => {
    const sourceInfo = sourceDefinitions.find(
      item => item.sourceDefinitionId === currentsource?.sourceDefinitionId
    );
    setErrorStatusRequest(0);
    try {
      await createConnection({
        values,
        source: currentsource,
        destinationId: destinations[0].destinationId,
        sourceDefinition: sourceInfo,
        destinationDefinition
      });

      push(Routes.Root);
    } catch (e) {
      setErrorStatusRequest(e.status);
    }
  };
  const renderStep = () => {
    if (currentStep === StepsTypes.CREATE_SOURCE) {
      return (
        <SourceStep
          onSubmit={onSubmitSourceStep}
          dropDownData={sourcesDropDownData}
          destinationDefinition={destinationDefinition}
          hasSuccess={successRequest}
          errorStatus={errorStatusRequest}
        />
      );
    }

    return (
      <ConnectionStep
        onSubmit={onSubmitConnectionStep}
        destinationDefinition={destinationDefinition}
        sourceDefinitionId={currentsource?.sourceDefinitionId || ""}
        sourceId={currentsource?.sourceId || ""}
      />
    );
  };

  const steps = [
    {
      id: StepsTypes.CREATE_SOURCE,
      name: <FormattedMessage id={"sources.selectSource"} />
    },
    {
      id: StepsTypes.SET_UP_CONNECTION,
      name: <FormattedMessage id={"onboarding.setUpConnection"} />
    }
  ];

  return (
    <>
      <PageTitle
        withLine
        title={<FormattedMessage id="sources.newSourceTitle" />}
        middleComponent={<StepsMenu data={steps} activeStep={currentStep} />}
      />
      <Content>{renderStep()}</Content>
    </>
  );
};

export default CreateSourcePage;
