import React from "react";

import ContentCard from "components/ContentCard";
import ServiceForm from "../ServiceForm";
import { JobsLogItem } from "components/JobItem";
import { ServiceFormProps } from "../ServiceForm/ServiceForm";

const ConnectorCard: React.FC<
  { title: React.ReactNode; jobInfo: any } & ServiceFormProps
> = ({ title, jobInfo, ...props }) => {
  return (
    <ContentCard title={title}>
      <ServiceForm {...props} />
      <JobsLogItem jobInfo={jobInfo} />
    </ContentCard>
  );
};

export { ConnectorCard };
