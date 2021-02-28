import React, { useMemo } from "react";
import styled from "styled-components";

import JobItem from "components/JobItem";
import { Job } from "core/resources/Job";

type IProps = {
  jobs: Job[];
};

const Content = styled.div``;

const JobsList: React.FC<IProps> = ({ jobs }) => {
  const sortJobs = useMemo(
    () => jobs.sort((a, b) => (a.job.createdAt > b.job.createdAt ? -1 : 1)),
    [jobs]
  );

  return (
    <Content>
      {sortJobs.map((item) => (
        <JobItem key={item.job.id} job={item.job} attempts={item.attempts} />
      ))}
    </Content>
  );
};

export default JobsList;
