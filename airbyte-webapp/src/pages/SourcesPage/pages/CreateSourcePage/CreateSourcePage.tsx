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
import DestinationImplementationResource from "../../../../core/resources/DestinationImplementation";
import config from "../../../../config";
import SourceResource from "../../../../core/resources/Source";
import DestinationResource from "../../../../core/resources/Destination";
import { SourceImplementation } from "../../../../core/resources/SourceImplementation";
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

  const { destinations } = useResource(
    DestinationImplementationResource.listShape(),
    {
      workspaceId: config.ui.workspaceId
    }
  );
  const currentDestination = destinations[0]; // Now we have only one destination. If we support multiple destinations we will fix this line
  const { sources } = useResource(SourceResource.listShape(), {
    workspaceId: config.ui.workspaceId
  });
  const destination = useResource(DestinationResource.detailShape(), {
    destinationId: currentDestination.destinationId
  });
  const { createSource } = useSource();
  const { createConnection } = useConnection();

  const [currentStep, setCurrentStep] = useState(StepsTypes.CREATE_SOURCE);

  const sourcesDropDownData = useMemo(
    () =>
      sources.map(item => ({
        text: item.name,
        value: item.sourceId,
        img: "/default-logo-catalog.svg"
      })),
    [sources]
  );

  const [
    currentSourceImplementation,
    setCurrentSourceImplementation
  ] = useState<SourceImplementation | undefined>(undefined);

  const onSubmitSourceStep = async (values: {
    name: string;
    serviceType: string;
    sourceId?: string;
    connectionConfiguration?: any;
  }) => {
    const connector = sources.find(
      item => item.sourceId === values.serviceType
    );
    setErrorStatusRequest(0);
    try {
      const result = await createSource({ values, sourceConnector: connector });
      setCurrentSourceImplementation(result);
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
    const sourceInfo = sources.find(
      item => item.sourceId === currentSourceImplementation?.sourceId
    );
    setErrorStatusRequest(0);
    try {
      await createConnection({
        values,
        sourceImplementation: currentSourceImplementation,
        destinationImplementationId:
          destinations[0].destinationImplementationId,
        sourceConnector: sourceInfo,
        destinationConnector: currentDestination
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
          destination={destination}
          hasSuccess={successRequest}
          errorStatus={errorStatusRequest}
        />
      );
    }

    return (
      <ConnectionStep
        onSubmit={onSubmitConnectionStep}
        destination={destination}
        sourceId={currentSourceImplementation?.sourceId || ""}
        sourceImplementationId={
          currentSourceImplementation?.sourceImplementationId || ""
        }
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
