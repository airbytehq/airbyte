import React, { useMemo } from "react";

import { JobItem } from "components/JobItem";
import { JobsWithJobs } from "components/JobItem/types";

import { JobWithAttemptsRead } from "core/request/AirbyteClient";

interface JobsListProps {
  jobs: JobWithAttemptsRead[];
}

const JobsList: React.FC<JobsListProps> = ({ jobs }) => {
  const sortJobs: JobsWithJobs[] = useMemo(
    () =>
      jobs.filter((job): job is JobsWithJobs => !!job.job).sort((a, b) => (a.job.createdAt > b.job.createdAt ? -1 : 1)),
    [jobs]
  );

  return (
    <div>
      {sortJobs.map((job) => (
        <JobItem key={job.job.id} job={job} />
      ))}
    </div>
  );
};

export default JobsList;
