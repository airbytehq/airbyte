import classNames from "classnames";
import { Line } from "rc-progress";
import { useIntl } from "react-intl";

import { getJobStatus } from "components/JobItem/JobItem";

import { AttemptRead, SynchronousJobRead } from "core/request/AirbyteClient";
import Status from "core/statuses";
import { JobsWithJobs } from "pages/ConnectionPage/pages/ConnectionItemPage/JobsList";

import styles from "./ProgressBar.module.scss";

function isJobsWithJobs(job: JobsWithJobs | SynchronousJobRead): job is JobsWithJobs {
  return (job as JobsWithJobs).attempts !== undefined;
}

export var ProgressBar = ({ job }: { job: JobsWithJobs | SynchronousJobRead }) => {
  const { formatMessage } = useIntl();

  let numerator = 0;
  let denominator = 0;
  let totalPercent = -1;
  let latestAttempt: AttemptRead | undefined;

  const jobStatus = getJobStatus(job);

  if (isJobsWithJobs(job)) {
    if (job.attempts) {
      latestAttempt = job.attempts[job.attempts?.length - 1];
      if (latestAttempt && latestAttempt.totalStats) {
        const totalStats = latestAttempt.totalStats;
        if (totalStats?.recordsEmitted && totalStats?.estimatedRecords) {
          numerator = totalStats.recordsEmitted;
          denominator = totalStats.estimatedRecords;
        }
      } else if (latestAttempt && !latestAttempt.totalStats && latestAttempt.streamStats) {
        for (const stream of latestAttempt.streamStats) {
          numerator += stream.stats.recordsEmitted ?? 0;
          denominator += stream.stats.estimatedRecords ?? 0;
        }
      }
    }
  } else {
    // TODO... maybe
  }

  totalPercent = (numerator / denominator) * 100;

  // colors from `_colors.scss` TODO: Use the SCSS variables maybe?
  let color = "white";
  switch (jobStatus) {
    case "pending":
      color = "#cbc8ff";
      break;
    case "running":
      color = "#cbc8ff";
      break;
    case "incomplete":
      color = "#fdf8e1";
      break;
    case "failed":
      color = "#e64228";
      break;
    case "succeeded":
      color = "#67dae1";
      totalPercent = 100; // just to be safe
      break;
    case "cancelled":
      totalPercent = 0; // just to be safe
      break;
  }

  return (
    <div className={classNames(styles.container)}>
      <Line percent={totalPercent} strokeColor={[color]} />
      {latestAttempt?.status === Status.RUNNING && latestAttempt.streamStats && (
        <>
          <div>
            {numerator} of {denominator} {formatMessage({ id: "estimate.syncedThusFar" })}
          </div>
          <div>
            <br />
            <div className={classNames(styles.container)}>Stream Stats:</div>
            {latestAttempt.streamStats?.map((stream) => {
              const localNumerator = stream.stats.recordsEmitted;
              const localDenominator = stream.stats.estimatedRecords;

              return (
                <div className={classNames(styles.container)}>
                  <strong>{stream.streamName}</strong> -{" "}
                  {localNumerator && localDenominator
                    ? `${Math.round(
                        (localNumerator * 100) / localDenominator
                      )}% complete (${localNumerator} / ${localDenominator} records moved)`
                    : `${localNumerator} records moved so far`}
                </div>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
};
