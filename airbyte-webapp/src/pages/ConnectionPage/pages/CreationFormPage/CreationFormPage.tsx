import React, { useState } from "react";
import { FormattedMessage } from "react-intl";

import { LoadingPage, PageTitle } from "components";
import ConnectionBlock from "components/ConnectionBlock";
import { FormPageContent } from "components/ConnectorBlocks";
import CreateConnectionContent from "components/CreateConnectionContent";
import DocumentationPanel from "components/DocumentationPanel/DocumentationPanel";
import HeadTitle from "components/HeadTitle";
import StepsMenu from "components/StepsMenu";

import { Connection } from "core/domain/connection";
import { Destination, DestinationDefinition, Source, SourceDefinition } from "core/domain/connector";
import { useGetDestination } from "hooks/services/useDestinationHook";
import { useGetSource } from "hooks/services/useSourceHook";
import useRouter from "hooks/useRouter";
import {
  useDestinationDefinition,
  useDestinationDefinitionList,
} from "services/connector/DestinationDefinitionService";
import { useGetDestinationDefinitionSpecificationAsync } from "services/connector/DestinationDefinitionSpecificationService";
import { useSourceDefinition, useSourceDefinitionList } from "services/connector/SourceDefinitionService";
import { useGetSourceDefinitionSpecificationAsync } from "services/connector/SourceDefinitionSpecificationService";
import { SidePanelStatusProvider } from "views/Connector/ConnectorDocumentationLayout/ConnectorDocumentationContext";
import { ConnectorDocumentationLayout } from "views/Connector/ConnectorDocumentationLayout/ConnectorDocumentationLayout";

import { ConnectionCreateDestinationForm } from "./components/DestinationForm";
import ExistingEntityForm from "./components/ExistingEntityForm";
import { ConnectionCreateSourceForm } from "./components/SourceForm";

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

const hasSourceId = (state: unknown): state is { sourceId: string } => {
  return typeof state === "object" && state !== null && typeof (state as { sourceId?: string }).sourceId === "string";
};

const hasDestinationId = (state: unknown): state is { destinationId: string } => {
  return (
    typeof state === "object" &&
    state !== null &&
    typeof (state as { destinationId?: string }).destinationId === "string"
  );
};

function usePreloadData(): {
  sourceDefinition?: SourceDefinition;
  destination?: Destination;
  source?: Source;
  destinationDefinition?: DestinationDefinition;
} {
  const { location } = useRouter();

  const source = useGetSource(hasSourceId(location.state) ? location.state.sourceId : null);

  const sourceDefinition = useSourceDefinition(source?.sourceDefinitionId);

  const destination = useGetDestination(hasDestinationId(location.state) ? location.state.destinationId : null);
  const destinationDefinition = useDestinationDefinition(destination?.destinationDefinitionId);

  return { source, sourceDefinition, destination, destinationDefinition };
}

export const CreationFormPage: React.FC = () => {
  const { location, push } = useRouter();

  const hasSourceDefinitionId = (state: unknown): state is { sourceDefinitionId: string } => {
    return (
      typeof state === "object" &&
      state !== null &&
      typeof (state as { sourceDefinitionId?: string }).sourceDefinitionId === "string"
    );
  };

  const [sourceDefinitionId, setSourceDefinitionId] = useState<string | null>(
    hasSourceDefinitionId(location.state) ? location.state.sourceDefinitionId : null
  );

  const { data: sourceDefinitionSpecification, error: sourceDefinitionError } =
    useGetSourceDefinitionSpecificationAsync(sourceDefinitionId);

  const hasDestinationDefinitionId = (state: unknown): state is { destinationDefinitionId: string } => {
    return (
      typeof state === "object" &&
      state !== null &&
      typeof (state as { destinationDefinitionId?: string }).destinationDefinitionId === "string"
    );
  };
  const [destinationDefinitionId, setDestinationDefinitionId] = useState<string | null>(
    hasDestinationDefinitionId(location.state) ? location.state.destinationDefinitionId : null
  );

  const { data: destinationDefinitionSpecification, error: destinationDefinitionError } =
    useGetDestinationDefinitionSpecificationAsync(destinationDefinitionId);

  // TODO: Probably there is a better way to figure it out instead of just checking third elem
  const locationType = location.pathname.split("/")[3];

  const type: EntityStepsTypes =
    locationType === "connections"
      ? EntityStepsTypes.CONNECTION
      : locationType === "source"
      ? EntityStepsTypes.DESTINATION
      : EntityStepsTypes.SOURCE;

  const hasConnectors = hasSourceId(location.state) && hasDestinationId(location.state);
  const [currentStep, setCurrentStep] = useState(
    hasConnectors ? StepsTypes.CREATE_CONNECTION : StepsTypes.CREATE_ENTITY
  );

  const [currentEntityStep, setCurrentEntityStep] = useState(
    hasSourceId(location.state) ? EntityStepsTypes.DESTINATION : EntityStepsTypes.SOURCE
  );

  const { destinationDefinition, sourceDefinition, source, destination } = usePreloadData();

  const onSelectExistingSource = (id: string) => {
    push("", {
      state: {
        ...(location.state as Record<string, unknown>),
        sourceId: id,
      },
    });
    setCurrentEntityStep(EntityStepsTypes.DESTINATION);
    setCurrentStep(StepsTypes.CREATE_CONNECTOR);
  };

  const onSelectExistingDestination = (id: string) => {
    push("", {
      state: {
        ...(location.state as Record<string, unknown>),
        destinationId: id,
      },
    });
    setCurrentEntityStep(EntityStepsTypes.CONNECTION);
    setCurrentStep(StepsTypes.CREATE_CONNECTION);
  };

  const { sourceDefinitions } = useSourceDefinitionList();
  const { destinationDefinitions } = useDestinationDefinitionList();

  const selectedService = destinationDefinitionId
    ? destinationDefinitions.find((item) => item.destinationDefinitionId === destinationDefinitionId)
    : sourceDefinitions.find((item) => item.sourceDefinitionId === sourceDefinitionId);

  const renderStep = () => {
    if (currentStep === StepsTypes.CREATE_ENTITY || currentStep === StepsTypes.CREATE_CONNECTOR) {
      if (currentEntityStep === EntityStepsTypes.SOURCE) {
        return (
          <>
            {type === EntityStepsTypes.CONNECTION && (
              <ExistingEntityForm type="source" onSubmit={onSelectExistingSource} />
            )}
            <>
              <ConnectionCreateSourceForm
                setSourceDefinitionId={setSourceDefinitionId}
                sourceDefinitionSpecification={sourceDefinitionSpecification}
                sourceDefinitionError={sourceDefinitionError}
                afterSubmit={() => {
                  if (type === "connection") {
                    setCurrentEntityStep(EntityStepsTypes.DESTINATION);
                    setCurrentStep(StepsTypes.CREATE_CONNECTOR);
                  } else {
                    setCurrentEntityStep(EntityStepsTypes.CONNECTION);
                    setCurrentStep(StepsTypes.CREATE_CONNECTION);
                  }
                }}
              />
            </>
          </>
        );
      } else if (currentEntityStep === EntityStepsTypes.DESTINATION) {
        return (
          <>
            {type === EntityStepsTypes.CONNECTION && (
              <ExistingEntityForm type="destination" onSubmit={onSelectExistingDestination} />
            )}
            <ConnectionCreateDestinationForm
              setDestinationDefinitionId={setDestinationDefinitionId}
              destinationDefinitionSpecification={destinationDefinitionSpecification}
              destinationDefinitionError={destinationDefinitionError}
              afterSubmit={() => {
                setCurrentEntityStep(EntityStepsTypes.CONNECTION);
                setCurrentStep(StepsTypes.CREATE_CONNECTION);
              }}
            />
          </>
        );
      }
    }

    const afterSubmitConnection = (connection: Connection) => {
      switch (type) {
        case EntityStepsTypes.DESTINATION:
          push(`../${source?.sourceId}`);
          break;
        case EntityStepsTypes.SOURCE:
          push(`../${destination?.destinationId}`);
          break;
        default:
          push(`../${connection.connectionId}`);
          break;
      }
    };

    if (!source || !destination) {
      console.error("unexpected state met");
      return <LoadingPage />;
    }

    return (
      <CreateConnectionContent
        source={source}
        destination={destination}
        afterSubmitConnection={afterSubmitConnection}
      />
    );
  };

  const steps =
    type === "connection"
      ? [
          {
            id: StepsTypes.CREATE_ENTITY,
            name: <FormattedMessage id="onboarding.createSource" />,
          },
          {
            id: StepsTypes.CREATE_CONNECTOR,
            name: <FormattedMessage id="onboarding.createDestination" />,
          },
          {
            id: StepsTypes.CREATE_CONNECTION,
            name: <FormattedMessage id="onboarding.setUpConnection" />,
          },
        ]
      : [
          {
            id: StepsTypes.CREATE_ENTITY,
            name:
              type === "destination" ? (
                <FormattedMessage id="onboarding.createDestination" />
              ) : (
                <FormattedMessage id="onboarding.createSource" />
              ),
          },
          {
            id: StepsTypes.CREATE_CONNECTION,
            name: <FormattedMessage id="onboarding.setUpConnection" />,
          },
        ];

  const titleId: string = (
    {
      [EntityStepsTypes.CONNECTION]: "connection.newConnectionTitle",
      [EntityStepsTypes.DESTINATION]: "destinations.newDestinationTitle",
      [EntityStepsTypes.SOURCE]: "sources.newSourceTitle",
    } as Record<EntityStepsTypes, string>
  )[type];

  return (
    <SidePanelStatusProvider>
      <HeadTitle titles={[{ id: "sources.newSourceTitle" }]} />
      <ConnectorDocumentationLayout>
        <>
          <PageTitle
            withLine
            title={<FormattedMessage id={titleId} />}
            middleComponent={<StepsMenu lightMode data={steps} activeStep={currentStep} />}
          />
          <FormPageContent big={currentStep === StepsTypes.CREATE_CONNECTION}>
            {currentStep !== StepsTypes.CREATE_CONNECTION && (!!source || !!destination) && (
              <ConnectionBlock
                itemFrom={source ? { name: source.name, icon: sourceDefinition?.icon } : undefined}
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
        </>
        <DocumentationPanel documentationUrl={selectedService?.documentationUrl || ""} />
      </ConnectorDocumentationLayout>
    </SidePanelStatusProvider>
  );
};
