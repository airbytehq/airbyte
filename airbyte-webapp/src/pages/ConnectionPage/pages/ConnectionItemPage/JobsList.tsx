import React, { useMemo } from "react";

import { JobItem } from "components/JobItem/JobItem";

import { JobWithAttemptsRead } from "core/request/AirbyteClient";

interface JobsListProps {
  jobs: JobWithAttemptsRead[];
}

export type JobsWithJobs = JobWithAttemptsRead & { job: Exclude<JobWithAttemptsRead["job"], undefined> };

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
