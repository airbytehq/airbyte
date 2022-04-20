import React, { useMemo } from "react";

import { JobItem } from "components/JobItem/JobItem";

import { JobWithAttemptsRead } from "../../../../../core/request/GeneratedApi";

type Props = {
  jobs: JobWithAttemptsRead[];
};

const JobsList: React.FC<Props> = ({ jobs }) => {
  const sortJobs = useMemo(
    () => jobs.filter((job) => job.job).sort((a, b) => (a.job!.createdAt > b.job!.createdAt ? -1 : 1)),
    [jobs]
  );

  return (
    <div>
      {sortJobs.map((item) => (
        <JobItem key={item.job!.id} job={item} />
      ))}
    </div>
  );
};

export default JobsList;
