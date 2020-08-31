import React, { useMemo, useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { useFetcher, useResource } from "rest-hooks";

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
import SourceImplementationResource, {
  SourceImplementation
} from "../../../../core/resources/SourceImplementation";

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
  const createSourcesImplementation = useFetcher(
    SourceImplementationResource.createShape()
  );
  const sourcesDropDownData = useMemo(
    () =>
      sources.map(item => ({
        text: item.name,
        value: item.sourceId,
        img: "/default-logo-catalog.svg"
      })),
    [sources]
  );

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
  const [currentStep, setCurrentStep] = useState(StepsTypes.CREATE_SOURCE);
  const [
    currentSourceImplementation,
    setCurrentSourceImplementation
  ] = useState<SourceImplementation | null>(null);

  const onSubmitSourceStep = async (values: {
    name: string;
    serviceType: string;
    specificationId?: string;
    connectionConfiguration?: any;
  }) => {
    setErrorStatusRequest(0);
    try {
      const result = await createSourcesImplementation(
        {},
        {
          workspaceId: config.ui.workspaceId,
          sourceSpecificationId: values.specificationId,
          connectionConfiguration: values.connectionConfiguration
        }
      );
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
  const onSubmitConnectionStep = () => push(Routes.Root);

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
      />
    );
  };

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
