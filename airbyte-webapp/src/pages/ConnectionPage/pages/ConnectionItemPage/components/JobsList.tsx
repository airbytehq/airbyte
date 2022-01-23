import React, { useMemo } from "react";

import JobItem from "components/JobItem";
import { JobListItem } from "core/domain/job/Job";

type IProps = {
  jobs: JobListItem[];
};

const JobsList: React.FC<IProps> = ({ jobs }) => {
  const sortJobs = useMemo(
    () => jobs.sort((a, b) => (a.job.createdAt > b.job.createdAt ? -1 : 1)),
    [jobs]
  );

  return (
    <div>
      {sortJobs.map((item) => (
        <JobItem key={item.job.id} job={item} />
      ))}
    </div>
  );
};

export default JobsList;
