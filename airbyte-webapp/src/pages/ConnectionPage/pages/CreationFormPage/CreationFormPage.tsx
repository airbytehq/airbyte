import React, { Suspense, useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import useRouter from "../../../../components/hooks/useRouterHook";
import MainPageWithScroll from "../../../../components/MainPageWithScroll";
import PageTitle from "../../../../components/PageTitle";
import StepsMenu from "../../../../components/StepsMenu";
import { FormPageContent } from "../../../../components/SourceAndDestinationsBlocks";
import CreateEntityView from "./components/CreateEntityView";
import SourceForm from "./components/SourceForm";
import DestinationForm from "./components/DestinationForm";
import ConnectionBlock from "../../../../components/ConnectionBlock";
import CreateConnection from "./components/CreateConnection";
import { IDataItem } from "../../../../components/DropDown/components/ListItem";
import { AnalyticsService } from "../../../../core/analytics/AnalyticsService";
import config from "../../../../config";
import { SyncSchema } from "../../../../core/resources/Schema";
import { Routes } from "../../../routes";
import useConnection from "../../../../components/hooks/services/useConnectionHook";
import ContentCard from "../../../../components/ContentCard";
import Spinner from "../../../../components/Spinner";
import { useResource } from "rest-hooks/lib/react-integration/hooks";
import SourceResource from "../../../../core/resources/Source";
import DestinationResource from "../../../../core/resources/Destination";

type IProps = {
  type: "source" | "destination";
};

export enum StepsTypes {
  CREATE_ENTITY = "createEntity",
  CREATE_CONNECTION = "createConnection"
}

export enum EntityStepsTypes {
  SOURCE = "source",
  DESTINATION = "destination",
  CONNECTION = "connection"
}

const SpinnerBlock = styled.div`
  margin: 40px;
  text-align: center;
`;

const FetchMessage = styled.div`
  font-size: 14px;
  line-height: 17px;
  color: ${({ theme }) => theme.textColor};
  margin-top: 15px;
  white-space: pre-line;
`;

const CreationFormPage: React.FC<IProps> = ({ type }) => {
  const { location, push }: any = useRouter();
  const source = useResource(
    SourceResource.detailShape(),
    location.state?.sourceId
      ? {
          sourceId: location.state.sourceId
        }
      : null
  );
  const destination = useResource(
    DestinationResource.detailShape(),
    location.state?.destinationId
      ? {
          destinationId: location.state.destinationId
        }
      : null
  );

  const { createConnection } = useConnection();
  const [errorStatusRequest, setErrorStatusRequest] = useState<number>(0);

  const steps = [
    {
      id: StepsTypes.CREATE_ENTITY,
      name:
        type === "destination" ? (
          <FormattedMessage id={"onboarding.createDestination"} />
        ) : (
          <FormattedMessage id={"onboarding.createSource"} />
        )
    },
    {
      id: StepsTypes.CREATE_CONNECTION,
      name: <FormattedMessage id={"onboarding.setUpConnection"} />
    }
  ];
  const [currentStep, setCurrentStep] = useState(StepsTypes.CREATE_ENTITY);
  const [currentEntityStep, setCurrentEntityStep] = useState(
    EntityStepsTypes.SOURCE
  );

  const onSelectFrequency = (item: IDataItem) => {
    AnalyticsService.track("New Connection - Action", {
      user_id: config.ui.workspaceId,
      action: "Select a frequency",
      frequency: item?.text,
      connector_source_definition: source?.name,
      connector_source_definition_id: source?.sourceDefinitionId,
      connector_destination_definition: destination?.name,
      connector_destination_definition_id: destination?.destinationDefinitionId
    });
  };

  const renderStep = () => {
    if (currentStep === StepsTypes.CREATE_ENTITY) {
      if (currentEntityStep === EntityStepsTypes.SOURCE) {
        if (location.state?.sourceId) {
          return (
            <CreateEntityView
              type="source"
              afterSuccess={() =>
                setCurrentEntityStep(EntityStepsTypes.DESTINATION)
              }
            />
          );
        }

        return (
          <SourceForm
            afterSubmit={() =>
              setCurrentEntityStep(EntityStepsTypes.DESTINATION)
            }
          />
        );
      } else if (currentEntityStep === EntityStepsTypes.DESTINATION) {
        if (location.state?.destinationId) {
          return (
            <CreateEntityView
              type="destination"
              afterSuccess={() => {
                setCurrentEntityStep(EntityStepsTypes.CONNECTION);
                setCurrentStep(StepsTypes.CREATE_CONNECTION);
              }}
            />
          );
        }

        return (
          <DestinationForm
            afterSubmit={() => {
              setCurrentEntityStep(EntityStepsTypes.CONNECTION);
              setCurrentStep(StepsTypes.CREATE_CONNECTION);
            }}
          />
        );
      }
    }

    const onSubmitConnectionStep = async (values: {
      frequency: string;
      syncSchema: SyncSchema;
    }) => {
      setErrorStatusRequest(0);
      try {
        await createConnection({
          values,
          source: source || undefined,
          destination: destination || undefined,
          sourceDefinition: {
            name: source?.name || "",
            sourceDefinitionId: source?.sourceDefinitionId || ""
          },
          destinationDefinition: {
            name: destination?.name || "",
            destinationDefinitionId: destination?.destinationDefinitionId || ""
          }
        });

        if (type === "destination") {
          push(`${Routes.Source}/${source?.sourceId}`);
        } else {
          push(`${Routes.Destination}/${destination?.destinationId}`);
        }
      } catch (e) {
        setErrorStatusRequest(e.status);
        console.log(e);
      }
    };

    const onSubmitStep = async (values: {
      frequency: string;
      syncSchema: SyncSchema;
    }) => {
      await onSubmitConnectionStep({
        ...values
      });
    };

    return (
      <ContentCard title={<FormattedMessage id="onboarding.setConnection" />}>
        <Suspense
          fallback={
            <SpinnerBlock>
              <Spinner />
              <FetchMessage>
                <FormattedMessage id="onboarding.fetchingSchema" />
              </FetchMessage>
            </SpinnerBlock>
          }
        >
          <CreateConnection
            sourceId={location.state?.sourceId}
            onSelectFrequency={onSelectFrequency}
            onSubmit={onSubmitStep}
            errorStatus={errorStatusRequest}
          />
        </Suspense>
      </ContentCard>
    );
  };

  return (
    <MainPageWithScroll
      title={
        <PageTitle
          withLine
          title={
            type === "destination" ? (
              <FormattedMessage id="destinations.newDestinationTitle" />
            ) : (
              <FormattedMessage id="sources.newSourceTitle" />
            )
          }
          middleComponent={
            <StepsMenu lightMode data={steps} activeStep={currentStep} />
          }
        />
      }
    >
      <FormPageContent>
        <ConnectionBlock
          itemFrom={source ? { name: source.name } : undefined}
          itemTo={destination ? { name: destination.name } : undefined}
        />
        {renderStep()}
      </FormPageContent>
    </MainPageWithScroll>
  );
};

export default CreationFormPage;
