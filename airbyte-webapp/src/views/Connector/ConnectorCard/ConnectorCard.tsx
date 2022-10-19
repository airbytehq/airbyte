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
import { ConnectorFormValues, ServiceForm, ServiceFormValues } from "views/Connector/ServiceForm";

import { useDocumentationPanelContext } from "../ConnectorDocumentationLayout/DocumentationPanelContext";
import { ConnectorServiceTypeControl } from "../ServiceForm/components/Controls/ConnectorServiceTypeControl";
import styles from "./ConnectorCard.module.scss";
import { useAnalyticsTrackFunctions } from "./useAnalyticsTrackFunctions";
import { useTestConnector } from "./useTestConnector";

// TODO: need to clean up the ConnectorCard and ServiceForm props,
// since some of props are used in both components, and some of them used just as a prop-drill
interface ConnectorCardBaseProps {
  title?: React.ReactNode;
  full?: boolean;
  jobInfo?: SynchronousJobRead | null;
  additionalSelectorComponent?: React.ReactNode;
  onSubmit: (values: ConnectorFormValues) => Promise<void> | void;
  onServiceSelect?: (id: string) => void;
  availableServices: ConnectorDefinition[];

  // used in ConnectorCard and ServiceForm
  formType: "source" | "destination";
  selectedConnectorDefinitionSpecification?: ConnectorDefinitionSpecification;
  isEditMode?: boolean;

  // used in ServiceForm
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

  const { selectedConnectorDefinitionSpecification, onServiceSelect, availableServices, isEditMode } = props;

  const selectedConnectorDefinitionSpecificationId =
    selectedConnectorDefinitionSpecification && ConnectorSpecification.id(selectedConnectorDefinitionSpecification);

  const selectedService = useMemo(
    () => availableServices.find((s) => Connector.id(s) === selectedConnectorDefinitionSpecificationId),
    [availableServices, selectedConnectorDefinitionSpecificationId]
  );

  // Handle Doc panel
  useEffect(() => {
    if (!selectedService) {
      return;
    }

    setDocumentationUrl(selectedService?.documentationUrl ?? "");
    setDocumentationPanelOpen(true);
  }, [selectedConnectorDefinitionSpecification, selectedService, setDocumentationPanelOpen, setDocumentationUrl]);

  const onHandleSubmit = async (values: ServiceFormValues) => {
    if (!selectedService) {
      return;
    }
    setErrorStatusRequest(null);
    setIsFormSubmitting(true);

    //  combine the "ServiceFormValues" and serviceType to make "ConnectorFormValues"
    const connectorFormValues: ConnectorFormValues = { ...values, serviceType: Connector.id(selectedService) };

    const testConnectorWithTracking = async () => {
      trackTestConnectorStarted(selectedService);
      try {
        await testConnector(connectorFormValues);
        trackTestConnectorSuccess(selectedService);
      } catch (e) {
        trackTestConnectorFailure(selectedService);
        throw e;
      }
    };

    try {
      await testConnectorWithTracking();
      onSubmit(connectorFormValues);
      setSaved(true);
    } catch (e) {
      setErrorStatusRequest(e);
      setIsFormSubmitting(false);
    }
  };

  const job = jobInfo || LogsRequestError.extractJobInfo(errorStatusRequest);

  // Fill form with existing connector values otherwise set the default service name
  const formValues = isEditMode ? props.connector : { name: selectedService?.name };

  return (
    <Card title={title} fullWidth={full}>
      <div className={styles.cardForm}>
        <div className={styles.connectorSelectControl}>
          <ConnectorServiceTypeControl
            formType={props.formType}
            onChangeServiceType={onServiceSelect}
            availableServices={availableServices}
            isEditMode={isEditMode}
            selectedServiceId={selectedConnectorDefinitionSpecificationId}
            disabled={isFormSubmitting}
          />
        </div>
        {additionalSelectorComponent}
        <div>
          <ServiceForm
            {...props}
            selectedService={selectedService}
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
