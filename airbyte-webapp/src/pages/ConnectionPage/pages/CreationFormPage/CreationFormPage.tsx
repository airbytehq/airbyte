import React, { useState } from "react";
// import { FormattedMessage } from "react-intl";
// import { useNavigate } from "react-router-dom";

import { LoadingPage } from "components";
// import ConnectionBlock from "components/ConnectionBlock";
import { ConnectionStep, CreateStepTypes } from "components/ConnectionStep";
import { FormPageContent } from "components/ConnectorBlocks";
import CreateConnectionContent from "components/CreateConnectionContent";
// import StepsMenu from "components/StepsMenu";
import HeadTitle from "components/HeadTitle";

import { useTrackPage, PageTrackingCodes } from "hooks/services/Analytics";
import { useGetDestination } from "hooks/services/useDestinationHook";
import { useGetSource } from "hooks/services/useSourceHook";
import useRouter from "hooks/useRouter";
import TestConnection from "pages/ConnectionPage/pages/CreationFormPage/components/TestConnection";
import { RoutePaths } from "pages/routePaths";
// import { useDestinationDefinition } from "services/connector/DestinationDefinitionService";
// import { useSourceDefinition } from "services/connector/SourceDefinitionService";
import { ConnectorDocumentationWrapper } from "views/Connector/ConnectorDocumentationLayout";
import { ServiceFormValues } from "views/Connector/ServiceForm/types";

import {
  DestinationDefinitionRead,
  DestinationRead,
  SourceDefinitionRead,
  SourceRead,
} from "../../../../core/request/AirbyteClient";
import { ConnectionCreateDestinationForm } from "./components/DestinationForm";
import { ConnectionCreateSourceForm } from "./components/SourceForm";

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

const hasCurrentStep = (state: unknown): state is { currentStep: string } => {
  return (
    typeof state === "object" && state !== null && typeof (state as { currentStep?: string }).currentStep === "string"
  );
};

function usePreloadData(): {
  sourceDefinition?: SourceDefinitionRead;
  destination?: DestinationRead;
  source?: SourceRead;
  destinationDefinition?: DestinationDefinitionRead;
} {
  const { location } = useRouter();

  const source = useGetSource(hasSourceId(location.state) ? location.state.sourceId : null);

  // const sourceDefinition = useSourceDefinition(source?.sourceDefinitionId);
  const destination = useGetDestination(hasDestinationId(location.state) ? location.state.destinationId : null);
  // const destinationDefinition = useDestinationDefinition(destination?.destinationDefinitionId);
  return { source, destination }; // sourceDefinition,destinationDefinition
}

export const CreationFormPage: React.FC<{
  backtrack?: boolean;
}> = ({ backtrack }) => {
  useTrackPage(PageTrackingCodes.CONNECTIONS_NEW);
  const { location, push } = useRouter();
  // const navigator = useNavigate();

  const [currentStep, setCurrentStep] = useState(
    hasCurrentStep(location.state) ? location.state.currentStep : CreateStepTypes.CREATE_SOURCE
  );

  const [currentEntityStep, setCurrentEntityStep] = useState(
    currentStep === CreateStepTypes.CREATE_SOURCE
      ? EntityStepsTypes.SOURCE
      : currentStep === CreateStepTypes.CREATE_DESTINATION
      ? EntityStepsTypes.DESTINATION
      : EntityStepsTypes.CONNECTION
  );

  const [isLoading, setLoadingStatus] = useState(true);
  const [fetchingConnectorError, setFetchingConnectorError] = useState<JSX.Element | string | null>(null);
  const [destinationFormValues, setDestinationFormValues] = useState<ServiceFormValues>({
    name: "",
    serviceType: "",
    connectionConfiguration: {},
  });

  const [sourceFormValues, setSourceFormValues] = useState<ServiceFormValues>({
    name: "",
    serviceType: "",
    connectionConfiguration: {},
  });

  const { source, destination } = usePreloadData();

  const handleTestingPageBackButton = () => {
    if (currentEntityStep === EntityStepsTypes.CONNECTION) {
      push("", {
        state: {
          ...(location.state as Record<string, unknown>),
          currentStep: CreateStepTypes.CREATE_CONNECTION,
        },
      });
    } else {
      if (currentEntityStep === EntityStepsTypes.SOURCE) {
        setCurrentStep(CreateStepTypes.CREATE_SOURCE);
      }
      if (currentEntityStep === EntityStepsTypes.DESTINATION) {
        setCurrentStep(CreateStepTypes.CREATE_DESTINATION);
      }
      push("", {
        state: {
          ...(location.state as Record<string, unknown>),
          currentStep,
        },
      });
    }
  };

  const renderStep = () => {
    if (currentStep === CreateStepTypes.CREATE_SOURCE || currentStep === CreateStepTypes.CREATE_DESTINATION) {
      if (currentEntityStep === EntityStepsTypes.SOURCE) {
        return (
          <FormPageContent>
            <ConnectionCreateSourceForm
              fetchingConnectorError={fetchingConnectorError}
              formValues={sourceFormValues}
              afterSubmit={() => {
                setLoadingStatus(false);
              }}
              onShowLoading={(
                isLoading: boolean,
                formValues: ServiceFormValues,
                error: JSX.Element | string | null
              ) => {
                setSourceFormValues(formValues);
                if (isLoading) {
                  setCurrentStep(CreateStepTypes.TEST_CONNECTION);
                  setLoadingStatus(true);
                } else {
                  setCurrentStep(CreateStepTypes.CREATE_SOURCE);
                  setFetchingConnectorError(error);
                }
              }}
              onBack={() => {
                // navigator(`../${RoutePaths.SelectConnection}`, {
                //   state: {
                //     ...(location.state as Record<string, unknown>),
                //     currentStep: CreateStepTypes.CREATE_SOURCE,
                //   },
                //   replace:true
                // });
                // navigator(-1);
                push(`../${RoutePaths.SelectConnection}`, {
                  state: {
                    ...(location.state as Record<string, unknown>),
                    currentStep: CreateStepTypes.CREATE_SOURCE,
                  },
                });
              }}
            />
          </FormPageContent>
        );
      } else if (currentEntityStep === EntityStepsTypes.DESTINATION) {
        return (
          <FormPageContent>
            <ConnectionCreateDestinationForm
              fetchingConnectorError={fetchingConnectorError}
              formValues={destinationFormValues}
              afterSubmit={() => {
                setLoadingStatus(false);
              }}
              onShowLoading={(
                isLoading: boolean,
                formValues: ServiceFormValues,
                error: JSX.Element | string | null
              ) => {
                setDestinationFormValues(formValues);
                if (isLoading) {
                  setCurrentStep(CreateStepTypes.TEST_CONNECTION);
                  setLoadingStatus(true);
                } else {
                  setCurrentStep(CreateStepTypes.CREATE_DESTINATION);
                  setFetchingConnectorError(error);
                }
              }}
              onBack={() => {
                push(`../${RoutePaths.SelectConnection}`, {
                  state: {
                    ...(location.state as Record<string, unknown>),
                    currentStep: CreateStepTypes.CREATE_DESTINATION,
                  },
                });
              }}
            />
          </FormPageContent>
        );
      }
    }

    const afterSubmitConnection = () => {
      setLoadingStatus(false);
      setCurrentStep(CreateStepTypes.ALL_FINISH);
    };

    const onListenAfterSubmit = (isSuccess: boolean) => {
      if (isSuccess) {
        setCurrentStep(CreateStepTypes.TEST_CONNECTION);
        setLoadingStatus(true);
      }
    };

    const hanldeFinishButton = () => {
      if (currentEntityStep === EntityStepsTypes.SOURCE) {
        if (backtrack) {
          setCurrentStep(CreateStepTypes.CREATE_CONNECTION);
          setCurrentEntityStep(EntityStepsTypes.CONNECTION);
          push("", {
            state: {
              ...(location.state as Record<string, unknown>),
              currentStep: CreateStepTypes.CREATE_CONNECTION,
            },
          });
          return;
        }
        push(`../${RoutePaths.SelectConnection}`, {
          state: {
            ...(location.state as Record<string, unknown>),
            currentStep: CreateStepTypes.CREATE_DESTINATION,
          },
        });
      }

      if (currentEntityStep === EntityStepsTypes.DESTINATION) {
        setCurrentStep(CreateStepTypes.CREATE_CONNECTION);
        setCurrentEntityStep(EntityStepsTypes.CONNECTION);
        push("", {
          state: {
            ...(location.state as Record<string, unknown>),
            currentStep: CreateStepTypes.CREATE_CONNECTION,
          },
        });
      }

      if (currentEntityStep === EntityStepsTypes.CONNECTION) {
        push(`/${RoutePaths.Connections}`);
      }
    };

    if (currentStep === CreateStepTypes.TEST_CONNECTION || currentStep === CreateStepTypes.ALL_FINISH) {
      return (
        <TestConnection
          type={currentEntityStep}
          isLoading={isLoading}
          onBack={handleTestingPageBackButton}
          onFinish={hanldeFinishButton}
        />
      );
    }

    if (!source || !destination) {
      console.error("unexpected state met");
      return <LoadingPage />;
    }

    return (
      <FormPageContent big={currentStep === CreateStepTypes.CREATE_CONNECTION}>
        <CreateConnectionContent
          onBack={() => {
            // navigator(-1);
            push(`../${RoutePaths.SelectConnection}`, {
              state: {
                ...(location.state as Record<string, unknown>),
                currentStep: CreateStepTypes.CREATE_DESTINATION,
              },
            });
          }}
          source={source}
          destination={destination}
          afterSubmitConnection={afterSubmitConnection}
          onListenAfterSubmit={onListenAfterSubmit}
        />
      </FormPageContent>
    );
  };
  return (
    <>
      <HeadTitle titles={[{ id: "connection.newConnectionTitle" }]} />
      <ConnectionStep lightMode type="connection" activeStep={currentStep} />
      <ConnectorDocumentationWrapper>{renderStep()}</ConnectorDocumentationWrapper>
    </>
  );
};
