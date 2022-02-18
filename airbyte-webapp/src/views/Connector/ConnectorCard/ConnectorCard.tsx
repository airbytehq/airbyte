import React from "react";

import { ContentCard } from "components";
import JobItem from "components/JobItem";

import ServiceForm from "../ServiceForm";
import { ServiceFormProps } from "../ServiceForm/ServiceForm";
import { JobInfo } from "core/domain/job/Job";

const ConnectorCard: React.FC<
  {
    title?: React.ReactNode;
    full?: boolean;
    jobInfo?: JobInfo | null;
  } & ServiceFormProps
> = ({ title, full, jobInfo, ...props }) => {
  return (
    <ContentCard title={title} full={full}>
      <ServiceForm {...props} />
      {jobInfo && <JobItem jobInfo={jobInfo} />}
    </ContentCard>
  );
};

export { ConnectorCard };
