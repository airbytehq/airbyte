import React, { useEffect, useMemo, useState } from "react";

import { Spinner } from "components/ui/Spinner";

import {
  Connector,
  ConnectorDefinition,
  ConnectorDefinitionSpecification,
  ConnectorSpecification,
  ConnectorT,
} from "core/domain/connector";
import { DestinationRead, SourceRead, SynchronousJobRead } from "core/request/AirbyteClient";
import { LogsRequestError } from "core/request/LogsRequestError";
import { generateMessageFromError } from "utils/errorStatusMessage";
import { ConnectorCardValues, ConnectorForm, ConnectorFormValues } from "views/Connector/ConnectorForm";

import { Controls } from "./components/Controls";
import ShowLoadingMessage from "./components/ShowLoadingMessage";
import styles from "./ConnectorCard.module.scss";
import { useAnalyticsTrackFunctions } from "./useAnalyticsTrackFunctions";
import { useTestConnector } from "./useTestConnector";
import { useDocumentationPanelContext } from "../ConnectorDocumentationLayout/DocumentationPanelContext";
import { ConnectorDefinitionTypeControl } from "../ConnectorForm/components/Controls/ConnectorServiceTypeControl";
import { FetchingConnectorError } from "../ConnectorForm/components/TestingConnectionError";

// TODO: need to clean up the ConnectorCard and ConnectorForm props,
// since some of props are used in both components, and some of them used just as a prop-drill
// https://github.com/airbytehq/airbyte/issues/18553
interface ConnectorCardBaseProps {
  title?: React.ReactNode;
  description?: React.ReactNode;
  full?: boolean;
  jobInfo?: SynchronousJobRead | null;
  additionalSelectorComponent?: React.ReactNode;
  onSubmit: (values: ConnectorCardValues) => Promise<void> | void;
  reloadConfig?: () => void;
  onDeleteClick?: () => void;
  onConnectorDefinitionSelect?: (id: string) => void;
  availableConnectorDefinitions: ConnectorDefinition[];

  // used in ConnectorCard and ConnectorForm
  formType: "source" | "destination";
  /**
   * id of the selected connector definition id - might be available even if the specification is not loaded yet
   * */
  selectedConnectorDefinitionId: string | null;
  selectedConnectorDefinitionSpecification?: ConnectorDefinitionSpecification;
  isEditMode?: boolean;

  // used in ConnectorForm
  formId?: string;
  fetchingConnectorError?: Error | null;
  isLoading?: boolean;
}

interface ConnectorCardCreateProps extends ConnectorCardBaseProps {
  isEditMode?: false;
}

interface ConnectorCardEditProps extends ConnectorCardBaseProps {
  isEditMode: true;
  connector: ConnectorT;
}

const getConnectorId = (connectorRead: DestinationRead | SourceRead) => {
  return "sourceId" in connectorRead ? connectorRead.sourceId : connectorRead.destinationId;
};

export const ConnectorCard: React.FC<ConnectorCardCreateProps | ConnectorCardEditProps> = ({
  jobInfo,
  onSubmit,
  onDeleteClick,
  additionalSelectorComponent,
  selectedConnectorDefinitionId,
  fetchingConnectorError,
  reloadConfig,
  ...props
}) => {
  const [errorStatusRequest, setErrorStatusRequest] = useState<Error | null>(null);
  const [isFormSubmitting, setIsFormSubmitting] = useState(false);

  const { setDocumentationUrl, setDocumentationPanelOpen } = useDocumentationPanelContext();
  const {
    testConnector,
    isTestConnectionInProgress,
    onStopTesting,
    error,
    reset,
    isSuccess: connectionTestSuccess,
  } = useTestConnector(props);
  const { trackTestConnectorFailure, trackTestConnectorSuccess, trackTestConnectorStarted } =
    useAnalyticsTrackFunctions(props.formType);

  useEffect(() => {
    // Whenever the selected connector changed, reset the check connection call and other errors
    reset();
    setErrorStatusRequest(null);
  }, [props.selectedConnectorDefinitionSpecification, reset]);

  const {
    selectedConnectorDefinitionSpecification,
    onConnectorDefinitionSelect,
    availableConnectorDefinitions,
    isEditMode,
  } = props;

  const selectedConnectorDefinitionSpecificationId =
    selectedConnectorDefinitionId ||
    (selectedConnectorDefinitionSpecification && ConnectorSpecification.id(selectedConnectorDefinitionSpecification));

  const selectedConnectorDefinition = useMemo(
    () => availableConnectorDefinitions.find((s) => Connector.id(s) === selectedConnectorDefinitionSpecificationId),
    [availableConnectorDefinitions, selectedConnectorDefinitionSpecificationId]
  );

  // Handle Doc panel
  useEffect(() => {
    if (!selectedConnectorDefinition) {
      return;
    }

    setDocumentationUrl(selectedConnectorDefinition?.documentationUrl ?? "");
    setDocumentationPanelOpen(true);
  }, [
    selectedConnectorDefinitionSpecification,
    selectedConnectorDefinition,
    setDocumentationPanelOpen,
    setDocumentationUrl,
  ]);

  const testConnectorWithTracking = async (connectorCardValues?: ConnectorCardValues) => {
    trackTestConnectorStarted(selectedConnectorDefinition);
    try {
      const response = await testConnector(connectorCardValues);
      trackTestConnectorSuccess(selectedConnectorDefinition);
      return response;
    } catch (e) {
      trackTestConnectorFailure(selectedConnectorDefinition);
      throw e;
    }
  };

  const handleTestConnector = async (values?: ConnectorCardValues) => {
    setErrorStatusRequest(null);
    try {
      await testConnectorWithTracking(values);
    } catch (e) {
      setErrorStatusRequest(e);
      throw e;
    }
  };

  const onHandleSubmit = async (values: ConnectorFormValues) => {
    if (!selectedConnectorDefinition) {
      return;
    }
    setErrorStatusRequest(null);
    setIsFormSubmitting(true);

    //  combine the "ConnectorFormValues" and serviceType to make "ConnectorFormValues"
    const connectorCardValues: ConnectorCardValues = {
      ...values,
      serviceType: Connector.id(selectedConnectorDefinition),
    };

    try {
      const response = await testConnectorWithTracking(connectorCardValues);
      if (response.jobInfo.connectorConfigurationUpdated && reloadConfig) {
        reloadConfig();
      } else {
        onSubmit(connectorCardValues);
      }
    } catch (e) {
      setErrorStatusRequest(e);
      setIsFormSubmitting(false);
      // keep throwing the exception to inform the component the submit did not go through
      throw e;
    }
  };

  const job = jobInfo || LogsRequestError.extractJobInfo(errorStatusRequest);

  const connector = isEditMode ? props.connector : undefined;

  // Fill form with existing connector values otherwise set the default service name
  const formValues = useMemo(
    () => (isEditMode && connector ? connector : { name: selectedConnectorDefinition?.name }),
    [isEditMode, connector, selectedConnectorDefinition?.name]
  );

  return (
    <ConnectorForm
      headerBlock={
        <>
          <div className={styles.connectorSelectControl}>
            <ConnectorDefinitionTypeControl
              formType={props.formType}
              isEditMode={isEditMode}
              disabled={isFormSubmitting}
              availableConnectorDefinitions={availableConnectorDefinitions}
              selectedConnectorDefinition={selectedConnectorDefinition}
              selectedConnectorDefinitionSpecificationId={selectedConnectorDefinitionSpecificationId}
              onChangeConnectorDefinition={onConnectorDefinitionSelect}
            />
          </div>
          {additionalSelectorComponent}
          {props.isLoading && (
            <div className={styles.loaderContainer}>
              <Spinner />
              <div className={styles.loadingMessage}>
                <ShowLoadingMessage connector={selectedConnectorDefinition?.name} />
              </div>
            </div>
          )}
          {fetchingConnectorError && <FetchingConnectorError />}
        </>
      }
      // Causes the whole ConnectorForm to be unmounted and a new instance mounted whenever the connector type changes.
      // That way we carry less state around inside it, preventing any state from one connector type from affecting another
      // connector type's form in any way.
      key={selectedConnectorDefinition && Connector.id(selectedConnectorDefinition)}
      {...props}
      selectedConnectorDefinition={selectedConnectorDefinition}
      selectedConnectorDefinitionSpecification={selectedConnectorDefinitionSpecification}
      isTestConnectionInProgress={isTestConnectionInProgress}
      connectionTestSuccess={connectionTestSuccess}
      onSubmit={onHandleSubmit}
      formValues={formValues}
      connectorId={isEditMode ? getConnectorId(props.connector) : undefined}
      renderFooter={({ dirty, isSubmitting, isValid, resetConnectorForm, getValues }) => (
        <Controls
          isEditMode={Boolean(isEditMode)}
          isTestConnectionInProgress={isTestConnectionInProgress}
          onCancelTesting={onStopTesting}
          isSubmitting={isSubmitting || isTestConnectionInProgress}
          errorMessage={error && generateMessageFromError(error)}
          formType={props.formType}
          hasDefinition={Boolean(selectedConnectorDefinitionId)}
          onRetestClick={() => {
            if (!selectedConnectorDefinitionId) {
              return;
            }
            handleTestConnector(
              isEditMode ? undefined : { ...getValues(), serviceType: selectedConnectorDefinitionId }
            );
          }}
          onDeleteClick={onDeleteClick}
          isValid={isValid}
          dirty={dirty}
          job={job ? job : undefined}
          onCancelClick={() => {
            resetConnectorForm();
          }}
          connectionTestSuccess={connectionTestSuccess}
        />
      )}
      renderWithCard
    />
  );
};
