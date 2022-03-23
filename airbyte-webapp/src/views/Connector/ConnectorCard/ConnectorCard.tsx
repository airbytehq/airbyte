import React, { useState } from "react";
import { FormattedMessage } from "react-intl";

import { ContentCard } from "components";
import JobItem from "components/JobItem";

import {
  ServiceForm,
  ServiceFormProps,
  ServiceFormValues,
} from "views/Connector/ServiceForm";
import { JobInfo } from "core/domain/job/Job";
import { LogsRequestError } from "core/request/LogsRequestError";
import { Scheduler } from "core/domain/connector";
import { createFormErrorMessage } from "utils/errorStatusMessage";
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
  } & Omit<ServiceFormProps, keyof ConnectorCardProvidedProps>
> = ({ title, full, jobInfo, onSubmit, ...props }) => {
  const [saved, setSaved] = useState(false);
  const [errorStatusRequest, setErrorStatusRequest] = useState<Error | null>(
    null
  );

  const {
    testConnector,
    isTestConnectionInProgress,
    onStopTesting,
    // isSuccess,
    error,
  } = useTestConnector(props);

  const onHandleSubmit = async (values: ServiceFormValues) => {
    setErrorStatusRequest(null);
    try {
      await testConnector(values);
      await onSubmit(values);

      setSaved(true);
    } catch (e) {
      setErrorStatusRequest(e);
    }
  };

  const jobInfoMapped =
    jobInfo || LogsRequestError.extractJobInfo(errorStatusRequest);

  return (
    <ContentCard title={title} full={full}>
      <ServiceForm
        {...props}
        errorMessage={
          props.errorMessage || (error && createFormErrorMessage(error))
        }
        isTestConnectionInProgress={isTestConnectionInProgress}
        onStopTesting={onStopTesting}
        testConnector={testConnector}
        onSubmit={onHandleSubmit}
        successMessage={
          props.successMessage ||
          (saved && props.isEditMode && (
            <FormattedMessage id="form.changesSaved" />
          ))
        }
      />
      {jobInfoMapped && <JobItem jobInfo={jobInfoMapped} />}
    </ContentCard>
  );
};

export { ConnectorCard };
