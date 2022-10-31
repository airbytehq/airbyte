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
  let timeRemainingString = "";
  let latestAttempt: AttemptRead | undefined;

  const jobStatus = getJobStatus(job);

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
      return null;
    case "succeeded":
      color = "#67dae1";
      return null;
    case "cancelled":
      return null;
  }

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

  totalPercent = Math.floor((numerator * 100) / denominator);

  if (latestAttempt && latestAttempt.status === Status.RUNNING) {
    const now = new Date().getTime();
    const elapsedTime = now - latestAttempt.createdAt * 1000;
    const timeRemaining = Math.floor(elapsedTime / totalPercent) * (100 - totalPercent); // in ms

    const minutesRemaining = Math.ceil(timeRemaining / 1000 / 60);
    const hoursRemaining = Math.ceil(minutesRemaining / 60);
    if (minutesRemaining <= 60) {
      timeRemainingString = `${minutesRemaining} minutes remaining`;
    } else {
      timeRemainingString = `${hoursRemaining} hours remaining`;
    }
  }

  return (
    <div className={classNames(styles.container)}>
      <Line percent={totalPercent} strokeColor={[color]} />
      {latestAttempt?.status === Status.RUNNING && latestAttempt.streamStats && (
        <>
          <div>
            {numerator} of {denominator} {formatMessage({ id: "estimate.syncedThusFar" })}{" "}
            {timeRemainingString.length > 0 ? ` ~ ${timeRemainingString}` : ""}
          </div>
          <div>
            <br />
            <div className={classNames(styles.container)}>Stream Stats:</div>
            {latestAttempt.streamStats?.map((stream, idx) => {
              const localNumerator = stream.stats.recordsEmitted;
              const localDenominator = stream.stats.estimatedRecords;

              return (
                <div className={classNames(styles.container)} key={`stream-progress-${idx}`}>
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
