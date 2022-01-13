import React from "react";

import { ContentCard } from "components";
import ServiceForm from "../ServiceForm";
import { ServiceFormProps } from "../ServiceForm/ServiceForm";
import { JobsLogItem } from "components/JobItem";

const ConnectorCard: React.FC<
  { title?: React.ReactNode; full?: boolean; jobInfo: any } & ServiceFormProps
> = ({ title, full, jobInfo, ...props }) => {
  return (
    <ContentCard title={title} full={full}>
      <ServiceForm {...props} />
      <JobsLogItem jobInfo={jobInfo} />
    </ContentCard>
  );
};

export { ConnectorCard };
