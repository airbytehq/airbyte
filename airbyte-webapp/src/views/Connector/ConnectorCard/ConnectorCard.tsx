import React, { useEffect, useMemo, useState } from "react";
import { FormattedMessage } from "react-intl";

import { JobItem } from "components/JobItem/JobItem";
import { Card } from "components/ui/Card";

import {
  Connector,
  ConnectorDefinition,
  ConnectorDefinitionSpecification,
  ConnectorSpecification,
  ConnectorT,
} from "core/domain/connector";
import { SynchronousJobRead } from "core/request/AirbyteClient";
import { LogsRequestError } from "core/request/LogsRequestError";
import { useAdvancedModeSetting } from "hooks/services/useAdvancedModeSetting";
import { generateMessageFromError } from "utils/errorStatusMessage";
import { ConnectorCardValues, ConnectorForm, ConnectorFormValues } from "views/Connector/ConnectorForm";

import { useDocumentationPanelContext } from "../ConnectorDocumentationLayout/DocumentationPanelContext";
import { ConnectorDefinitionTypeControl } from "../ConnectorForm/components/Controls/ConnectorServiceTypeControl";
import styles from "./ConnectorCard.module.scss";
import { useAnalyticsTrackFunctions } from "./useAnalyticsTrackFunctions";
import { useTestConnector } from "./useTestConnector";

// TODO: need to clean up the ConnectorCard and ConnectorForm props,
// since some of props are used in both components, and some of them used just as a prop-drill
// https://github.com/airbytehq/airbyte/issues/18553
interface ConnectorCardBaseProps {
  title?: React.ReactNode;
  full?: boolean;
  jobInfo?: SynchronousJobRead | null;
  additionalSelectorComponent?: React.ReactNode;
  onSubmit: (values: ConnectorCardValues) => Promise<void> | void;
  onConnectorDefinitionSelect?: (id: string) => void;
  availableConnectorDefinitions: ConnectorDefinition[];

  // used in ConnectorCard and ConnectorForm
  formType: "source" | "destination";
  selectedConnectorDefinitionSpecification?: ConnectorDefinitionSpecification;
  isEditMode?: boolean;

  // used in ConnectorForm
  formId?: string;
  fetchingConnectorError?: Error | null;
  errorMessage?: React.ReactNode;
  successMessage?: React.ReactNode;
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

export const ConnectorCard: React.FC<ConnectorCardCreateProps | ConnectorCardEditProps> = ({
  title,
  full,
  jobInfo,
  onSubmit,
  additionalSelectorComponent,
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
    selectedConnectorDefinitionSpecification && ConnectorSpecification.id(selectedConnectorDefinitionSpecification);

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
    }
  };

  const job = jobInfo || LogsRequestError.extractJobInfo(errorStatusRequest);

  // Fill form with existing connector values otherwise set the default service name
  const formValues = isEditMode ? props.connector : { name: selectedConnectorDefinition?.name };

  return (
    <Card title={title} fullWidth={full}>
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
          <ConnectorForm
            {...props}
            selectedConnectorDefinition={selectedConnectorDefinition}
            selectedConnectorDefinitionSpecification={selectedConnectorDefinitionSpecification}
            isTestConnectionInProgress={isTestConnectionInProgress}
            onStopTesting={onStopTesting}
            testConnector={testConnector}
            onSubmit={onHandleSubmit}
            formValues={formValues}
            errorMessage={props.errorMessage || (error && generateMessageFromError(error))}
            successMessage={
              props.successMessage || (saved && props.isEditMode && <FormattedMessage id="form.changesSaved" />)
            }
          />
          {/* Show the job log only if advanced mode is turned on or the actual job failed (not the check inside the job) */}
          {job && (advancedMode || !job.succeeded) && <JobItem job={job} />}
        </div>
      </div>
    </Card>
  );
};
