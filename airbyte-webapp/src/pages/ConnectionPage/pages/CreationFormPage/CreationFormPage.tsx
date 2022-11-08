import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import { useLocation, useNavigate } from "react-router-dom";

import { LoadingPage } from "components";
import { CloudInviteUsersHint } from "components/CloudInviteUsersHint";
import { HeadTitle } from "components/common/HeadTitle";
import ConnectionBlock from "components/ConnectionBlock";
import { FormPageContent } from "components/ConnectorBlocks";
import { CreateConnectionForm } from "components/CreateConnection/CreateConnectionForm";
import { PageHeader } from "components/ui/PageHeader";
import { StepsMenu } from "components/ui/StepsMenu";

import {
  DestinationDefinitionRead,
  DestinationRead,
  SourceDefinitionRead,
  SourceRead,
} from "core/request/AirbyteClient";
import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { useFormChangeTrackerService } from "hooks/services/FormChangeTracker";
import { useGetDestination } from "hooks/services/useDestinationHook";
import { useGetSource } from "hooks/services/useSourceHook";
import { useLocationState } from "hooks/useLocationState";
import { useDestinationDefinition } from "services/connector/DestinationDefinitionService";
import { useSourceDefinition } from "services/connector/SourceDefinitionService";
import { ConnectorDocumentationWrapper } from "views/Connector/ConnectorDocumentationLayout";

import { ConnectionCreateDestinationForm } from "./ConnectionCreateDestinationForm";
import { ConnectionCreateSourceForm } from "./ConnectionCreateSourceForm";
import ExistingEntityForm from "./ExistingEntityForm";

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
  sourceDefinition?: SourceDefinitionRead;
  destination?: DestinationRead;
  source?: SourceRead;
  destinationDefinition?: DestinationDefinitionRead;
} {
  const location = useLocation();

  const source = useGetSource(hasSourceId(location.state) ? location.state.sourceId : null);

  const sourceDefinition = useSourceDefinition(source?.sourceDefinitionId);

  const destination = useGetDestination(hasDestinationId(location.state) ? location.state.destinationId : null);
  const destinationDefinition = useDestinationDefinition(destination?.destinationDefinitionId);

  return { source, sourceDefinition, destination, destinationDefinition };
}

export const CreationFormPage: React.FC = () => {
  useTrackPage(PageTrackingCodes.CONNECTIONS_NEW);
  const location = useLocation();

  // exp-signup-selected-source-definition
  const state = useLocationState<{ sourceDefinitionId?: string }>();
  const isSourceDefinitionSelected = Boolean(state?.sourceDefinitionId);

  const navigate = useNavigate();
  const { clearAllFormChanges } = useFormChangeTrackerService();

  // TODO: Probably there is a better way to figure it out instead of just checking third elem
  const locationType = location.pathname.split("/")[3];

  const type: EntityStepsTypes =
    locationType === "connections"
      ? EntityStepsTypes.CONNECTION
      : locationType === "source"
      ? EntityStepsTypes.DESTINATION
      : EntityStepsTypes.SOURCE;

  const [currentStep, setCurrentStep] = useState(
    hasSourceId(location.state) && hasDestinationId(location.state)
      ? StepsTypes.CREATE_CONNECTION
      : hasSourceId(location.state) && !hasDestinationId(location.state)
      ? StepsTypes.CREATE_CONNECTOR
      : StepsTypes.CREATE_ENTITY
  );

  const [currentEntityStep, setCurrentEntityStep] = useState(
    hasSourceId(location.state) ? EntityStepsTypes.DESTINATION : EntityStepsTypes.SOURCE
  );

  const { destinationDefinition, sourceDefinition, source, destination } = usePreloadData();

  const onSelectExistingSource = (id: string) => {
    clearAllFormChanges();
    navigate("", {
      state: {
        ...(location.state as Record<string, unknown>),
        sourceId: id,
      },
    });
    setCurrentEntityStep(EntityStepsTypes.DESTINATION);
    setCurrentStep(StepsTypes.CREATE_CONNECTOR);
  };

  const onSelectExistingDestination = (id: string) => {
    clearAllFormChanges();
    navigate("", {
      state: {
        ...(location.state as Record<string, unknown>),
        destinationId: id,
      },
    });
    setCurrentEntityStep(EntityStepsTypes.CONNECTION);
    setCurrentStep(StepsTypes.CREATE_CONNECTION);
  };

  const renderStep = () => {
    if (currentStep === StepsTypes.CREATE_ENTITY || currentStep === StepsTypes.CREATE_CONNECTOR) {
      if (currentEntityStep === EntityStepsTypes.SOURCE) {
        return (
          <>
            {/* // exp-signup-selected-source-definition */}
            {type === EntityStepsTypes.CONNECTION && !isSourceDefinitionSelected && (
              <ExistingEntityForm type="source" onSubmit={onSelectExistingSource} />
            )}
            <ConnectionCreateSourceForm
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
            <CloudInviteUsersHint connectorType="source" />
          </>
        );
      } else if (currentEntityStep === EntityStepsTypes.DESTINATION) {
        return (
          <>
            {type === EntityStepsTypes.CONNECTION && (
              <ExistingEntityForm type="destination" onSubmit={onSelectExistingDestination} />
            )}
            <ConnectionCreateDestinationForm
              afterSubmit={() => {
                setCurrentEntityStep(EntityStepsTypes.CONNECTION);
                setCurrentStep(StepsTypes.CREATE_CONNECTION);
              }}
            />
            <CloudInviteUsersHint connectorType="destination" />
          </>
        );
      }
    }

    if (!source || !destination) {
      console.error("unexpected state met");
      return <LoadingPage />;
    }

    return <CreateConnectionForm source={source} destination={destination} />;
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
    <>
      <HeadTitle titles={[{ id: "connection.newConnectionTitle" }]} />
      <ConnectorDocumentationWrapper>
        <PageHeader
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
      </ConnectorDocumentationWrapper>
    </>
  );
};
