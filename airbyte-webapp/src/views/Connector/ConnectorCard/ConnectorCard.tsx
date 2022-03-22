import React, { useState } from "react";

import { ContentCard } from "components";
import JobItem from "components/JobItem";

import ServiceForm from "../ServiceForm";
import { ServiceFormProps } from "../ServiceForm/ServiceForm";
import { JobInfo } from "core/domain/job/Job";
import { ServiceFormValues } from "../ServiceForm/types";
import { LogsRequestError } from "core/request/LogsRequestError";
import { FormattedMessage } from "react-intl";

const ConnectorCard: React.FC<
  {
    title?: React.ReactNode;
    full?: boolean;
    jobInfo?: JobInfo | null;
  } & ServiceFormProps
> = ({ title, full, jobInfo, ...props }) => {
  const [saved, setSaved] = useState(false);
  const [errorStatusRequest, setErrorStatusRequest] = useState<Error | null>(
    null
  );
  const onSubmit = async (values: ServiceFormValues) => {
    setErrorStatusRequest(null);
    try {
      await props.onSubmit(values);

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
        onSubmit={onSubmit}
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
