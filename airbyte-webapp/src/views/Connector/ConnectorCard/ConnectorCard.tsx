import React, { useState } from "react";
import { FormattedMessage } from "react-intl";

import { ContentCard } from "components";
import JobItem from "components/JobItem";

import { Connector, ConnectorT, Scheduler } from "core/domain/connector";
import { JobInfo } from "core/domain/job/Job";
import { LogsRequestError } from "core/request/LogsRequestError";
import { useAnalytics } from "hooks/services/Analytics";
import { createFormErrorMessage } from "utils/errorStatusMessage";
import { ServiceForm, ServiceFormProps, ServiceFormValues } from "views/Connector/ServiceForm";

import { useTestConnector } from "./useTestConnector";

export type ConnectorCardProvidedProps = {
  isTestConnectionInProgress: boolean;
  isSuccess: boolean;
  onStopTesting: () => void;
  testConnector: (v?: ServiceFormValues) => Promise<Scheduler>;
};

const ConnectorCard: React.FC<
  {
    title?: React.ReactNode;
    full?: boolean;
    jobInfo?: JobInfo | null;
  } & Omit<ServiceFormProps, keyof ConnectorCardProvidedProps> &
    (
      | {
          isEditMode: true;
          connector: ConnectorT;
        }
      | { isEditMode?: false }
    )
> = ({ title, full, jobInfo, onSubmit, ...props }) => {
  const [saved, setSaved] = useState(false);
  const [errorStatusRequest, setErrorStatusRequest] = useState<Error | null>(null);

  const { testConnector, isTestConnectionInProgress, onStopTesting, error } = useTestConnector(props);

  const analyticsService = useAnalytics().service;

  const onHandleSubmit = async (values: ServiceFormValues) => {
    setErrorStatusRequest(null);

    const connector = props.availableServices.find((item) => Connector.id(item) === values.serviceType);

    try {
      if (connector) {
        if (props.formType === "source") {
          analyticsService.track("New Source - Action", {
            action: "Test a connector",
            connector_source: connector?.name,
            connector_source_definition_id: Connector.id(connector),
          });
        } else {
          analyticsService.track("New Destination - Action", {
            action: "Test a connector",
            connector_destination: connector?.name,
            connector_destination_definition_id: Connector.id(connector),
          });
        }
      }

      await testConnector(values);
      await onSubmit(values);

      setSaved(true);
    } catch (e) {
      setErrorStatusRequest(e);
    }
  };

  const jobInfoMapped = jobInfo || LogsRequestError.extractJobInfo(errorStatusRequest);

  return (
    <ContentCard title={title} full={full}>
      <ServiceForm
        {...props}
        errorMessage={props.errorMessage || (error && createFormErrorMessage(error))}
        isTestConnectionInProgress={isTestConnectionInProgress}
        onStopTesting={onStopTesting}
        testConnector={testConnector}
        onSubmit={onHandleSubmit}
        successMessage={
          props.successMessage || (saved && props.isEditMode && <FormattedMessage id="form.changesSaved" />)
        }
      />
      {jobInfoMapped && <JobItem jobInfo={jobInfoMapped} />}
    </ContentCard>
  );
};

export { ConnectorCard };
