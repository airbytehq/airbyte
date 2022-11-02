import classNames from "classnames";
import { Line } from "rc-progress";
import { useIntl, FormattedMessage } from "react-intl";

import { getJobStatus } from "components/JobItem/JobItem";

import { AttemptRead, JobConfigType, SynchronousJobRead } from "core/request/AirbyteClient";
import Status from "core/statuses";
import { JobsWithJobs } from "pages/ConnectionPage/pages/ConnectionItemPage/JobsList";

import styles from "./ProgressBar.module.scss";

function isJobsWithJobs(job: JobsWithJobs | SynchronousJobRead): job is JobsWithJobs {
  return (job as JobsWithJobs).attempts !== undefined;
}

const formatBytes = (bytes?: number) => {
  if (!bytes) {
    return <FormattedMessage id="sources.countBytes" values={{ count: bytes || 0 }} />;
  }

  const k = 1024;
  const dm = 2;
  const sizes = ["Bytes", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  const result = parseFloat((bytes / Math.pow(k, i)).toFixed(dm));

  return <FormattedMessage id={`sources.count${sizes[i]}`} values={{ count: result }} />;
};

export const ProgressBar = ({
  job,
  jobConfigType,
}: {
  job: JobsWithJobs | SynchronousJobRead;
  jobConfigType: JobConfigType;
}) => {
  const { formatMessage, formatNumber } = useIntl();

  if (jobConfigType !== "sync") {
    return null;
  }

  let numeratorRecords = -1;
  let denominatorRecords = -1;
  let totalPercentRecords = -1;
  let numeratorBytes = -1;
  let denominatorBytes = -1;
  // let totalPercentBytes = -1;
  let elapsedTimeMS = -1;
  let timeRemaining = -1;
  let timeRemainingString = "";
  const unEstimatedStreams: string[] = [];
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
      let countTotalsFromStreams = true;
      if (
        latestAttempt.totalStats?.recordsEmitted &&
        latestAttempt.totalStats?.estimatedRecords &&
        latestAttempt.totalStats?.bytesEmitted &&
        latestAttempt.totalStats?.estimatedBytes
      ) {
        countTotalsFromStreams = false;
        numeratorRecords = latestAttempt.totalStats.recordsEmitted;
        denominatorRecords = latestAttempt.totalStats.estimatedRecords;
        numeratorBytes = latestAttempt.totalStats.bytesEmitted;
        denominatorBytes = latestAttempt.totalStats.estimatedBytes;
      }

      if (latestAttempt && !latestAttempt.totalStats && latestAttempt.streamStats) {
        for (const stream of latestAttempt.streamStats) {
          if (!stream.stats.recordsEmitted) {
            unEstimatedStreams.push(`${stream.streamName}`);
          }
          if (countTotalsFromStreams) {
            numeratorRecords += stream.stats.recordsEmitted ?? 0;
            denominatorRecords += stream.stats.estimatedRecords ?? 0;
            numeratorBytes += stream.stats.bytesEmitted ?? 0;
            denominatorBytes += stream.stats.estimatedBytes ?? 0;
          }
        }
      }
    }
  } else {
    // TODO... maybe
  }

  totalPercentRecords = denominatorRecords > 0 ? Math.floor((numeratorRecords * 100) / denominatorRecords) : 0;

  // chose to estimate time remaining based on records rather than bytes
  if (latestAttempt && latestAttempt.status === Status.RUNNING) {
    elapsedTimeMS = new Date().getTime() - latestAttempt.createdAt * 1000;
    timeRemaining = Math.floor(elapsedTimeMS / totalPercentRecords) * (100 - totalPercentRecords); // in ms
    const minutesRemaining = Math.ceil(timeRemaining / 1000 / 60);
    const hoursRemaining = Math.ceil(minutesRemaining / 60);
    if (minutesRemaining <= 60) {
      timeRemainingString = `${minutesRemaining} ${formatMessage({ id: "estimate.minutesRemaining" })}`;
    } else {
      timeRemainingString = `${hoursRemaining} ${formatMessage({ id: "estimate.hoursRemaining" })}`;
    }
  }

  return (
    <div className={classNames(styles.container)}>
      {unEstimatedStreams.length === 0 && <Line percent={totalPercentRecords} strokeColor={[color]} />}
      {latestAttempt?.status === Status.RUNNING && (
        <>
          {unEstimatedStreams.length === 0 && (
            <div>
              {totalPercentRecords}% {timeRemaining < Infinity && timeRemaining > 0 ? `| ~${timeRemainingString}` : ""}
            </div>
          )}
          {unEstimatedStreams.length > 0 && (
            <div>
              {unEstimatedStreams.length} {formatMessage({ id: "estimate.unEstimatedStreams" })}
            </div>
          )}
          {denominatorRecords > 0 && (
            <>
              <div>
                {formatNumber(numeratorRecords)}{" "}
                {unEstimatedStreams.length > 0 ? "" : `/ ${formatNumber(denominatorRecords)}`}{" "}
                {formatMessage({ id: "estimate.recordsSynced" })} @{" "}
                {Math.round((numeratorRecords / elapsedTimeMS) * 1000)}{" "}
                {formatMessage({ id: "estimate.recordsPerSecond" })}
              </div>
              <div>
                {formatBytes(numeratorBytes)}{" "}
                {unEstimatedStreams.length > 0 ? (
                  ""
                ) : (
                  <>
                    <span>/ </span>
                    {formatBytes(denominatorBytes)}
                  </>
                )}{" "}
                {formatMessage({ id: "estimate.bytesSynced" })} @ {formatBytes((numeratorBytes * 1000) / elapsedTimeMS)}
                {formatMessage({ id: "estimate.bytesPerSecond" })}
              </div>
            </>
          )}

          {latestAttempt.streamStats && (
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
                      ? `${Math.round((localNumerator * 100) / localDenominator)}${formatMessage({
                          id: "estimate.percentComplete",
                        })} (${formatNumber(localNumerator)} / ${formatNumber(localDenominator)} ${formatMessage({
                          id: "estimate.recordsSynced",
                        })})`
                      : `${localNumerator} ${formatMessage({ id: "estimate.recordsSyncedThusFar" })} (no estimate)`}
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}
    </div>
  );
};
