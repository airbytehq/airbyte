import React, { useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { useLocation, useNavigate } from "react-router-dom";

import { LoadingPage } from "components";
import { CloudInviteUsersHint } from "components/CloudInviteUsersHint";
import { HeadTitle } from "components/common/HeadTitle";
import { ConnectionBlock } from "components/connection/ConnectionBlock";
import { CreateConnectionForm } from "components/connection/CreateConnectionForm";
import { FormPageContent } from "components/ConnectorBlocks";
import { PageHeader } from "components/ui/PageHeader";
import { StepsIndicator } from "components/ui/StepsIndicator";

import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { useFormChangeTrackerService } from "hooks/services/FormChangeTracker";
import { InlineEnrollmentCallout } from "packages/cloud/components/experiments/FreeConnectorProgram/InlineEnrollmentCallout";
import { ConnectorDocumentationWrapper } from "views/Connector/ConnectorDocumentationLayout";

import { ConnectionCreateDestinationForm } from "./ConnectionCreateDestinationForm";
import { ConnectionCreateSourceForm } from "./ConnectionCreateSourceForm";
import ExistingEntityForm from "./ExistingEntityForm";
import { hasDestinationId, hasSourceId, usePreloadData } from "./usePreloadData";

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
          <InlineEnrollmentCallout withBottomMargin />
          {renderStep()}
        </FormPageContent>
      </ConnectorDocumentationWrapper>
    </>
  );
};
