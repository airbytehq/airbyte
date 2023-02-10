import React, { useState, useEffect } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { useLocation, useNavigate, useSearchParams } from "react-router-dom";

import { LoadingPage } from "components";
import { CloudInviteUsersHint } from "components/CloudInviteUsersHint";
import { HeadTitle } from "components/common/HeadTitle";
import { ConnectionBlock } from "components/connection/ConnectionBlock";
import { CreateConnectionForm } from "components/connection/CreateConnectionForm";
import { FormPageContent } from "components/ConnectorBlocks";
import { PageHeader } from "components/ui/PageHeader";
import { StepsIndicator } from "components/ui/StepsIndicator";

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
import { InlineEnrollmentCallout } from "packages/cloud/components/experiments/FreeConnectorProgram/InlineEnrollmentCallout";
import { useDestinationDefinition } from "services/connector/DestinationDefinitionService";
import { useSourceDefinition } from "services/connector/SourceDefinitionService";
import { ConnectorDocumentationWrapper } from "views/Connector/ConnectorDocumentationLayout";

import { ConnectionCreateDestinationForm } from "./ConnectionCreateDestinationForm";
import { ConnectionCreateSourceForm } from "./ConnectionCreateSourceForm";
import ExistingEntityForm from "./ExistingEntityForm";

enum StepsTypes {
  CREATE_ENTITY = "createEntity",
  CREATE_CONNECTOR = "createConnector",
  CREATE_CONNECTION = "createConnection",
}

enum EntityStepsTypes {
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
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  const sourceIdFromLocationState = hasSourceId(location.state) && location.state.sourceId;
  const sourceIdFromSearchParams = searchParams.get("sourceId");
  const sourceId = sourceIdFromLocationState || sourceIdFromSearchParams;

  /**
   * There are two places we may find a sourceId, depending on the scenario. This effect
   * keeps them in sync according to the following logic:
   *   0) if `location.state.sourceId` and the `sourceId` query param are both unset or
   *      are both set to the same value, then we don't need to take any action.
   *   1) else if `location.state.sourceId` exists, we arrived at this page via the legacy
   *      internal "routing" system, meaning there has been a user interaction
   *      specifically selecting that source. This is the highest precedence source of
   *      truth, so if it exists we explicitly set the sourceId query param to match it.
   *   2) else if there's a `sourceId` query param, we arrived at this page via a fresh
   *      page load. This logic was added to support the airbyte-cloud's free connector
   *      program enrollment flow: it involves a round-trip visit to a Stripe domain,
   *      which wipes location.state. We explicitly navigate to the current path
   *      (including the current query string) with `location.state.sourceId` set.
   */
  useEffect(() => {
    if (sourceIdFromLocationState && sourceIdFromSearchParams === sourceIdFromLocationState) {
      // sourceId is set and everything is in sync, no further action needed
    } else if (sourceIdFromLocationState) {
      sourceId && setSearchParams({ sourceId });
    } else if (sourceIdFromSearchParams) {
      // we have to simultaneously set both the query string and location.state to avoid
      // an infinite mutually recursive rerender loop:
      //   A: set location.state and rerender; GOTO B
      //   B: set query param and rerender; GOTO A
      navigate(`${location.search}`, { state: { sourceId }, replace: true });
    } else {
      // sourceId is unset and everything is in sync, no further action needed
    }
  }, [sourceIdFromLocationState, sourceIdFromSearchParams, setSearchParams, navigate, sourceId, location.search]);
  const source = useGetSource(sourceId);

  const sourceDefinition = useSourceDefinition(source?.sourceDefinitionId);

  const destination = useGetDestination(hasDestinationId(location.state) ? location.state.destinationId : null);
  const destinationDefinition = useDestinationDefinition(destination?.destinationDefinitionId);

  return { source, sourceDefinition, destination, destinationDefinition };
}

export const CreateConnectionPage: React.FC = () => {
  useTrackPage(PageTrackingCodes.CONNECTIONS_NEW);
  const location = useLocation();
  const { formatMessage } = useIntl();

  const navigate = useNavigate();
  const { clearAllFormChanges } = useFormChangeTrackerService();

  // TODO: select UI and behavior based on the route using, you know, the router
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
            {type === EntityStepsTypes.CONNECTION && (
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
            {source && <InlineEnrollmentCallout withBottomMargin />}
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
            name: formatMessage({ id: "onboarding.createSource" }),
          },
          {
            id: StepsTypes.CREATE_CONNECTOR,
            name: formatMessage({ id: "onboarding.createDestination" }),
          },
          {
            id: StepsTypes.CREATE_CONNECTION,
            name: formatMessage({ id: "onboarding.setUpConnection" }),
          },
        ]
      : [
          {
            id: StepsTypes.CREATE_ENTITY,
            name:
              type === "destination"
                ? formatMessage({ id: "onboarding.createDestination" })
                : formatMessage({ id: "onboarding.createSource" }),
          },
          {
            id: StepsTypes.CREATE_CONNECTION,
            name: formatMessage({ id: "onboarding.setUpConnection" }),
          },
        ];

  const titleId: string =
    currentStep === "createConnection"
      ? "connection.newConnectionTitle"
      : (
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
          middleComponent={<StepsIndicator steps={steps} activeStep={currentStep} />}
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
