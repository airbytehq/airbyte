import React, { useEffect, useMemo, useState } from "react";
import { FormattedMessage } from "react-intl";

import { JobItem } from "components/JobItem/JobItem";
import { Card } from "components/ui/Card";
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
import { useAdvancedModeSetting } from "hooks/services/useAdvancedModeSetting";
import { generateMessageFromError } from "utils/errorStatusMessage";
import { ConnectorCardValues, ConnectorForm, ConnectorFormValues } from "views/Connector/ConnectorForm";

import { useDocumentationPanelContext } from "../ConnectorDocumentationLayout/DocumentationPanelContext";
import { ConnectorDefinitionTypeControl } from "../ConnectorForm/components/Controls/ConnectorServiceTypeControl";
import { FetchingConnectorError } from "../ConnectorForm/components/TestingConnectionError";
import ShowLoadingMessage from "./components/ShowLoadingMessage";
import styles from "./ConnectorCard.module.scss";
import { useAnalyticsTrackFunctions } from "./useAnalyticsTrackFunctions";
import { useTestConnector } from "./useTestConnector";

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
  hasSuccess?: boolean;
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
  title,
  description,
  full,
  jobInfo,
  onSubmit,
  additionalSelectorComponent,
  selectedConnectorDefinitionId,
  fetchingConnectorError,
  ...props
}) => {
  const [saved, setSaved] = useState(false);
  const [errorStatusRequest, setErrorStatusRequest] = useState<Error | null>(null);
  const [isFormSubmitting, setIsFormSubmitting] = useState(false);
  const [advancedMode] = useAdvancedModeSetting();

  const { setDocumentationUrl, setDocumentationPanelOpen } = useDocumentationPanelContext();
  const { testConnector, isTestConnectionInProgress, onStopTesting, error, reset } = useTestConnector(props);
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

    const testConnectorWithTracking = async () => {
      trackTestConnectorStarted(selectedConnectorDefinition);
      try {
        await testConnector(connectorCardValues);
        trackTestConnectorSuccess(selectedConnectorDefinition);
      } catch (e) {
        trackTestConnectorFailure(selectedConnectorDefinition);
        throw e;
      }
    };

    try {
      await testConnectorWithTracking();
      onSubmit(connectorCardValues);
      setSaved(true);
    } catch (e) {
      setErrorStatusRequest(e);
      setIsFormSubmitting(false);
      // keep throwing the exception to inform the component the submit did not go through
      throw e;
    }
  };

  const job = jobInfo || LogsRequestError.extractJobInfo(errorStatusRequest);

  // Fill form with existing connector values otherwise set the default service name
  const formValues = isEditMode ? props.connector : { name: selectedConnectorDefinition?.name };

  return (
    <Card title={title} description={description} fullWidth={full}>
      <div className={styles.cardForm}>
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
        <div>
          {props.isLoading && (
            <div className={styles.loaderContainer}>
              <Spinner />
              <div className={styles.loadingMessage}>
                <ShowLoadingMessage connector={selectedConnectorDefinition?.name} />
              </div>
            </div>
          )}
          {fetchingConnectorError && <FetchingConnectorError />}
          {selectedConnectorDefinition && selectedConnectorDefinitionSpecification && (
            <ConnectorForm
              // Causes the whole ConnectorForm to be unmounted and a new instance mounted whenever the connector type changes.
              // That way we carry less state around inside it, preventing any state from one connector type from affecting another
              // connector type's form in any way.
              key={selectedConnectorDefinition && Connector.id(selectedConnectorDefinition)}
              {...props}
              selectedConnectorDefinition={selectedConnectorDefinition}
              selectedConnectorDefinitionSpecification={selectedConnectorDefinitionSpecification}
              isTestConnectionInProgress={isTestConnectionInProgress}
              onStopTesting={onStopTesting}
              testConnector={testConnector}
              onSubmit={onHandleSubmit}
              formValues={formValues}
              errorMessage={error && generateMessageFromError(error)}
              successMessage={saved && props.isEditMode && <FormattedMessage id="form.changesSaved" />}
              connectorId={isEditMode ? getConnectorId(props.connector) : undefined}
            />
          )}
          {/* Show the job log only if advanced mode is turned on or the actual job failed (not the check inside the job) */}
          {job && (advancedMode || !job.succeeded) && <JobItem job={job} />}
        </div>
      </div>
    </Card>
  );
};
