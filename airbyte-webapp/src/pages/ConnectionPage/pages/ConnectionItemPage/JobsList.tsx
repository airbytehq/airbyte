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
      jobs
        .filter((job): job is JobsWithJobs => !!job.job)
        .sort((a, b) => (a.job.createdAt > b.job.createdAt ? -1 : 1))
        .map((value, index) => {
          // TODO: Remove before merging
          if (index !== 0 || !value.attempts) {
            return value;
          }

          value.job.status = "running";

          value.attempts[0].bytesSynced = 500000000;
          value.attempts[0].recordsSynced = 12178;
          value.attempts[0].totalStats = {
            bytesEmitted: 40000000,
            estimatedBytes: 10232100,
            recordsEmitted: 1123,
            recordsCommitted: 110,
            estimatedRecords: 5500,
            stateMessagesEmitted: 5,
          };

          value.attempts[0].status = "running";
          value.attempts[0].streamStats = [
            {
              streamName: "pokemon",
              stats: {},
            },
          ];
          value.attempts[0].streamStats = [
            {
              streamName: "pokemon",
              stats: {
                bytesEmitted: 1000200,
                estimatedBytes: 13000000,
                recordsEmitted: 120,
                recordsCommitted: 100,
                estimatedRecords: 1238,
              },
            },
            {
              streamName: "pokemon2",
              stats: {
                bytesEmitted: 1000200,
                estimatedBytes: 13000000,
                recordsEmitted: 12,
                recordsCommitted: 100,
                estimatedRecords: 1238,
              },
            },
            {
              streamName: "pokemon3",
              stats: {
                bytesEmitted: 1000200,
                estimatedBytes: 13000000,
                recordsEmitted: 1238,
                recordsCommitted: 1238,
                estimatedRecords: 1238,
              },
            },
            {
              streamName: "pokemon4",
              stats: {
                bytesEmitted: 1000200,
                estimatedBytes: 13000000,
                recordsEmitted: 560,
                recordsCommitted: 100,
                estimatedRecords: 1238,
              },
            },
            {
              streamName: "pokemon5",
              stats: {
                bytesEmitted: 1000200,
                estimatedBytes: 13000000,
                recordsEmitted: 1200,
                recordsCommitted: 100,
                estimatedRecords: 1238,
              },
            },
            {
              streamName: "pokemon200",
              stats: {
                bytesEmitted: 1000200,
                estimatedBytes: 13000000,
                recordsEmitted: 120,
                recordsCommitted: 100,
                estimatedRecords: 1238,
              },
            },
            {
              streamName: "pokemon200",
              stats: {
                bytesEmitted: 1000200,
                estimatedBytes: 13000000,
                recordsEmitted: 120,
                recordsCommitted: 100,
                estimatedRecords: 1238,
              },
            },
            {
              streamName: "pokemon200",
              stats: {
                bytesEmitted: 1000200,
                estimatedBytes: 13000000,
                recordsEmitted: 120,
                recordsCommitted: 100,
                estimatedRecords: 1238,
              },
            },
            {
              streamName: "pokemon200",
              stats: {
                bytesEmitted: 1000200,
                estimatedBytes: 13000000,
                recordsEmitted: 120,
                recordsCommitted: 100,
                estimatedRecords: 1238,
              },
            },
            {
              streamName: "pokemon200",
              stats: {
                bytesEmitted: 1000200,
                estimatedBytes: 13000000,
                recordsEmitted: 120,
                recordsCommitted: 100,
                estimatedRecords: 1238,
              },
            },
            {
              streamName: "pokemon200",
              stats: {
                bytesEmitted: 1000200,
                estimatedBytes: 13000000,
                recordsEmitted: 120,
                recordsCommitted: 100,
                estimatedRecords: 1238,
              },
            },
            {
              streamName: "pokemon200",
              stats: {
                bytesEmitted: 1000200,
                estimatedBytes: 13000000,
                recordsEmitted: 120,
                recordsCommitted: 100,
                estimatedRecords: 1238,
              },
            },
            {
              streamName: "pokemon200",
              stats: {
                bytesEmitted: 1000200,
                estimatedBytes: 13000000,
                recordsEmitted: 120,
                recordsCommitted: 100,
                estimatedRecords: 1238,
              },
            },
            {
              streamName: "pokemon200",
              stats: {
                bytesEmitted: 1000200,
                estimatedBytes: 13000000,
                recordsEmitted: 120,
                recordsCommitted: 100,
                estimatedRecords: 1238,
              },
            },
            {
              streamName: "pokemon200",
              stats: {
                bytesEmitted: 1000200,
                estimatedBytes: 13000000,
                recordsEmitted: 120,
                recordsCommitted: 100,
                estimatedRecords: 1238,
              },
            },
            {
              streamName: "some_longer_stream_name",
              stats: {
                bytesEmitted: 1000200,
                recordsEmitted: 120,
                recordsCommitted: 100,
              },
            },
          ];

          return value;
        }),
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
