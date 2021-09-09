import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import { useResource } from "rest-hooks";

import useRouter from "hooks/useRouter";
import MainPageWithScroll from "components/MainPageWithScroll";
import PageTitle from "components/PageTitle";
import StepsMenu from "components/StepsMenu";
import { FormPageContent } from "components/ConnectorBlocks";
import CreateEntityView from "./components/CreateEntityView";
import SourceForm from "./components/SourceForm";
import DestinationForm from "./components/DestinationForm";
import ConnectionBlock from "components/ConnectionBlock";
import { Routes } from "../../../routes";
import CreateConnectionContent from "components/CreateConnectionContent";
import SourceResource from "core/resources/Source";
import DestinationResource from "core/resources/Destination";
import DestinationDefinitionResource from "core/resources/DestinationDefinition";
import SourceDefinitionResource from "core/resources/SourceDefinition";
import HeadTitle from "components/HeadTitle";

type IProps = {
  type: "source" | "destination" | "connection";
};

export enum StepsTypes {
  CREATE_ENTITY = "createEntity",
  CREATE_CONNECTOR = "createConnector",
  CREATE_CONNECTION = "createConnection",
}

export enum EntityStepsTypes {
  SOURCE = "source",
  DESTINATION = "destination",
  CONNECTION = "connection",
}

const CreationFormPage: React.FC<IProps> = ({ type }) => {
  const [currentStep, setCurrentStep] = useState(StepsTypes.CREATE_ENTITY);
  const [currentEntityStep, setCurrentEntityStep] = useState(
    EntityStepsTypes.SOURCE
  );

  const { location, push } = useRouter();
  const source = useResource(
    SourceResource.detailShape(),
    location.state?.sourceId
      ? {
          sourceId: location.state.sourceId,
        }
      : null
  );
  const sourceDefinition = useResource(
    SourceDefinitionResource.detailShape(),
    source
      ? {
          sourceDefinitionId: source.sourceDefinitionId,
        }
      : null
  );

  const destination = useResource(
    DestinationResource.detailShape(),
    location.state?.destinationId
      ? {
          destinationId: location.state.destinationId,
        }
      : null
  );
  const destinationDefinition = useResource(
    DestinationDefinitionResource.detailShape(),
    destination
      ? {
          destinationDefinitionId: destination.destinationDefinitionId,
        }
      : null
  );

  const renderStep = () => {
    if (
      currentStep === StepsTypes.CREATE_ENTITY ||
      currentStep === StepsTypes.CREATE_CONNECTOR
    ) {
      if (currentEntityStep === EntityStepsTypes.SOURCE) {
        if (location.state?.sourceId) {
          return (
            <CreateEntityView
              type="source"
              afterSuccess={() => {
                setCurrentEntityStep(EntityStepsTypes.DESTINATION);
                if (type === "connection") {
                  setCurrentStep(StepsTypes.CREATE_CONNECTOR);
                }
              }}
            />
          );
        }

        return (
          <SourceForm
            afterSubmit={() => {
              setCurrentEntityStep(EntityStepsTypes.DESTINATION);
              if (type === "connection") {
                setCurrentStep(StepsTypes.CREATE_CONNECTOR);
              }
            }}
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

    const afterSubmitConnection = () => {
      if (type === "destination") {
        push(`${Routes.Source}/${source?.sourceId}`);
      } else if (type === "source") {
        push(`${Routes.Destination}/${destination?.destinationId}`);
      } else {
        push(`${Routes.Connections}`);
      }
    };

    return (
      <CreateConnectionContent
        source={source!}
        destination={destination!}
        afterSubmitConnection={afterSubmitConnection}
      />
    );
  };

  const steps =
    type === "connection"
      ? [
          {
            id: StepsTypes.CREATE_ENTITY,
            name: <FormattedMessage id={"onboarding.createSource"} />,
          },
          {
            id: StepsTypes.CREATE_CONNECTOR,
            name: <FormattedMessage id={"onboarding.createDestination"} />,
          },
          {
            id: StepsTypes.CREATE_CONNECTION,
            name: <FormattedMessage id={"onboarding.setUpConnection"} />,
          },
        ]
      : [
          {
            id: StepsTypes.CREATE_ENTITY,
            name:
              type === "destination" ? (
                <FormattedMessage id={"onboarding.createDestination"} />
              ) : (
                <FormattedMessage id={"onboarding.createSource"} />
              ),
          },
          {
            id: StepsTypes.CREATE_CONNECTION,
            name: <FormattedMessage id={"onboarding.setUpConnection"} />,
          },
        ];

  const titleId = () => {
    switch (type) {
      case "connection":
        return "connection.newConnectionTitle";
      case "destination":
        return "destinations.newDestinationTitle";
      case "source":
        return "sources.newSourceTitle";
    }
  };

  return (
    <MainPageWithScroll
      headTitle={<HeadTitle titles={[{ id: titleId() }]} />}
      pageTitle={
        <PageTitle
          withLine
          title={<FormattedMessage id={titleId()} />}
          middleComponent={
            <StepsMenu lightMode data={steps} activeStep={currentStep} />
          }
        />
      }
    >
      <FormPageContent big={currentStep === StepsTypes.CREATE_CONNECTION}>
        {currentStep !== StepsTypes.CREATE_CONNECTION &&
          (!!source || !!destination) && (
            <ConnectionBlock
              itemFrom={
                source
                  ? { name: source.name, icon: sourceDefinition?.icon }
                  : undefined
              }
              itemTo={
                destination
                  ? {
                      name: destination.name,
                      icon: destinationDefinition?.icon,
                    }
                  : undefined
              }
            />
          )}
        {renderStep()}
      </FormPageContent>
    </MainPageWithScroll>
  );
};

export default CreationFormPage;
