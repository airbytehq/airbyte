import classNames from "classnames";
import { useIntl } from "react-intl";

import { getJobStatus } from "components/JobItem/JobItem";
import { Text } from "components/ui/Text";

import { AttemptRead, AttemptStatus, SynchronousJobRead } from "core/request/AirbyteClient";
import { JobsWithJobs } from "pages/ConnectionPage/pages/ConnectionItemPage/JobsList";
import { formatBytes } from "utils/numberHelper";

import styles from "./JobProgress.module.scss";
import { ProgressLine } from "./JobProgressLine";
import { StreamProgress } from "./StreamProgress";
import { progressBarCalculations } from "./utils";

function isJobsWithJobs(job: JobsWithJobs | SynchronousJobRead): job is JobsWithJobs {
  return "attempts" in job;
}

interface ProgressBarProps {
  job: JobsWithJobs | SynchronousJobRead;
  expanded?: boolean;
}

export const JobProgress: React.FC<ProgressBarProps> = ({ job, expanded }) => {
  const { formatMessage, formatNumber } = useIntl();

  let latestAttempt: AttemptRead | undefined;
  if (isJobsWithJobs(job) && job.attempts) {
    latestAttempt = job.attempts[job.attempts.length - 1];
  }
  if (!latestAttempt) {
    return null;
  }

  const jobStatus = getJobStatus(job);
  if (["failed", "succeeded", "cancelled"].includes(jobStatus)) {
    return null;
  }

  const {
    displayProgressBar,
    totalPercentRecords,
    timeRemaining,
    numeratorBytes,
    numeratorRecords,
    denominatorRecords,
    denominatorBytes,
    unEstimatedStreams,
    elapsedTimeMS,
  } = progressBarCalculations(latestAttempt);

  let timeRemainingString = "";
  if (elapsedTimeMS && timeRemaining) {
    const minutesRemaining = Math.ceil(timeRemaining / 1000 / 60);
    const hoursRemaining = Math.ceil(minutesRemaining / 60);
    if (minutesRemaining <= 60) {
      timeRemainingString = formatMessage({ id: "connection.progress.minutesRemaining" }, { value: minutesRemaining });
    } else {
      timeRemainingString = formatMessage({ id: "connection.progress.hoursRemaining" }, { value: hoursRemaining });
    }
  }

  return (
    <Text as="div" size="xs">
      {displayProgressBar && (
        <ProgressLine percent={totalPercentRecords} type={jobStatus === "incomplete" ? "warning" : "default"} />
      )}
      {latestAttempt?.status === AttemptStatus.running && (
        <>
          {displayProgressBar && (
            <div>
              {totalPercentRecords}% {timeRemaining < Infinity && timeRemaining > 0 ? `| ${timeRemainingString}` : ""}
            </div>
          )}
          {!displayProgressBar && unEstimatedStreams.length > 0 && (
            <div>{formatMessage({ id: "estimate.unEstimatedStreams" }, { count: unEstimatedStreams.length })}</div>
          )}
          {denominatorRecords > 0 && (
            <>
              <div>
                {formatNumber(numeratorRecords)} {displayProgressBar ? "" : `/ ${formatNumber(denominatorRecords)}`}{" "}
                {formatMessage({ id: "estimate.recordsSynced" }, { value: numeratorRecords })} @{" "}
                {Math.round((numeratorRecords / elapsedTimeMS) * 1000)}{" "}
                {formatMessage({ id: "estimate.recordsPerSecond" })}
              </div>
              <div>
                {formatBytes(numeratorBytes)}{" "}
                {displayProgressBar && (
                  <>
                    <span>/ </span>
                    {formatBytes(denominatorBytes)}
                  </>
                )}{" "}
                {formatMessage({ id: "estimate.bytesSynced" })} @ {formatBytes((numeratorBytes * 1000) / elapsedTimeMS)}
                {formatMessage({ id: "estimate.perSecond" })}
              </div>
            </>
          )}

          {latestAttempt.streamStats && (
            <div className={classNames(styles.streams, { [styles.open]: expanded })}>
              {latestAttempt.streamStats?.map((stream) => {
                return <StreamProgress stream={stream} key={stream.streamName} />;
                // const localNumerator = stream.stats.recordsEmitted;
                // const localDenominator = stream.stats.estimatedRecords;
                // return (
                //   <Text size="xs" as="div" key={`stream-progress-${idx}`}>
                //     <strong>{stream.streamName}</strong> -{" "}
                //     {localNumerator && localDenominator
                //       ? `${Math.round((localNumerator * 100) / localDenominator)}${formatMessage({
                //           id: "estimate.percentComplete",
                //         })} (${formatNumber(localNumerator)} / ${formatNumber(localDenominator)} ${formatMessage(
                //           { id: "estimate.recordsSynced" },
                //           { value: localNumerator }
                //         )})`
                //       : `${localNumerator} ${formatMessage(
                //           { id: "estimate.recordsSynced" },
                //           { value: localNumerator }
                //         )} (${formatMessage({
                //           id: "estimate.noEstimate",
                //         })})`}
                //   </Text>
                // );
              })}
            </div>
          )}
        </>
      )}
    </Text>
  );
};
