import React from "react";
import styled from "styled-components";

import JobItem from "./JobItem";
import { Job } from "../../../../../core/resources/Job";

type IProps = {
  jobs: Job[];
};

const Content = styled.div``;

const JobsList: React.FC<IProps> = ({ jobs }) => {
  console.log(jobs);
  return (
    <Content>
      {jobs.map(item => (
        <JobItem key={item.job.id} job={item.job} attempts={item.attempts} />
      ))}
    </Content>
  );
};

export default JobsList;
