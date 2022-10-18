import React, { useEffect, useState } from "react";
import { FormattedMessage } from "react-intl";

import { JobItem } from "components/JobItem/JobItem";
import { Card } from "components/ui/Card";

import { Connector, ConnectorSpecification, ConnectorT } from "core/domain/connector";
import { SynchronousJobRead } from "core/request/AirbyteClient";
import { LogsRequestError } from "core/request/LogsRequestError";
import { useAdvancedModeSetting } from "hooks/services/useAdvancedModeSetting";
import { generateMessageFromError } from "utils/errorStatusMessage";
import { ServiceForm, ServiceFormProps, ServiceFormValues } from "views/Connector/ServiceForm";

import { ConnectorServiceTypeControl } from "../ServiceForm/components/Controls/ConnectorServiceTypeControl";
import styles from "./ConnectorCard.module.scss";
import { useAnalyticsTrackFunctions } from "./useAnalyticsTrackFunctions";
import { useTestConnector } from "./useTestConnector";

type ConnectorCardProvidedProps = Omit<
  ServiceFormProps,
  "isKeyConnectionInProgress" | "isSuccess" | "onStopTesting" | "testConnector"
>;

interface ConnectorCardBaseProps extends ConnectorCardProvidedProps {
  title?: React.ReactNode;
  full?: boolean;
  jobInfo?: SynchronousJobRead | null;
  additionalSelectorComponent?: React.ReactNode;
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

  const { testConnector, isTestConnectionInProgress, onStopTesting, error, reset } = useTestConnector(props);
  const { trackTestConnectorFailure, trackTestConnectorSuccess, trackTestConnectorStarted } =
    useAnalyticsTrackFunctions(props.formType);

  useEffect(() => {
    // Whenever the selected connector changed, reset the check connection call and other errors
    reset();
    setErrorStatusRequest(null);
  }, [props.selectedConnectorDefinitionSpecification, reset]);

  const onHandleSubmit = async (values: ServiceFormValues) => {
    setErrorStatusRequest(null);
    setIsFormSubmitting(true);

    const connector = props.availableServices.find((item) => Connector.id(item) === values.serviceType);

    const testConnectorWithTracking = async () => {
      trackTestConnectorStarted(connector);
      try {
        await testConnector(values);
        trackTestConnectorSuccess(connector);
      } catch (e) {
        trackTestConnectorFailure(connector);
        throw e;
      }
    };

    try {
      await testConnectorWithTracking();
      onSubmit(values);
      setSaved(true);
    } catch (e) {
      setErrorStatusRequest(e);
      setIsFormSubmitting(false);
    }
  };

  const job = jobInfo || LogsRequestError.extractJobInfo(errorStatusRequest);

  const { selectedConnectorDefinitionSpecification, onServiceSelect, availableServices, isEditMode } = props;
  const selectedConnectorDefinitionSpecificationId =
    selectedConnectorDefinitionSpecification && ConnectorSpecification.id(selectedConnectorDefinitionSpecification);

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
            errorMessage={props.errorMessage || (error && generateMessageFromError(error))}
            isTestConnectionInProgress={isTestConnectionInProgress}
            onStopTesting={onStopTesting}
            testConnector={testConnector}
            onSubmit={onHandleSubmit}
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
