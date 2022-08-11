import { faAngleDown } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import React from "react";
import { FormattedDateParts, FormattedMessage, FormattedTimeParts } from "react-intl";

import { StatusIcon } from "components";
import { Cell, Row } from "components/SimpleTableComponents";

import { AttemptRead, JobStatus } from "core/request/AirbyteClient";
import { SynchronousJobReadWithStatus } from "core/request/LogsRequestError";
import { JobsWithJobs } from "pages/ConnectionPage/pages/ConnectionItemPage/components/JobsList";

import { getJobStatus } from "../JobItem";
import AttemptDetails from "./AttemptDetails";
import styles from "./MainInfo.module.scss";

const getJobConfig = (job: SynchronousJobReadWithStatus | JobsWithJobs) =>
  (job as SynchronousJobReadWithStatus).configType ?? (job as JobsWithJobs).job.configType;

const getJobCreatedAt = (job: SynchronousJobReadWithStatus | JobsWithJobs) =>
  (job as SynchronousJobReadWithStatus).createdAt ?? (job as JobsWithJobs).job.createdAt;

const partialSuccessCheck = (attempts: AttemptRead[]) => {
  if (attempts.length > 0 && attempts[attempts.length - 1].status === JobStatus.failed) {
    return attempts.some((attempt) => attempt.failureSummary && attempt.failureSummary.partialSuccess);
  }
  return false;
};

interface MainInfoProps {
  job: SynchronousJobReadWithStatus | JobsWithJobs;
  attempts?: AttemptRead[];
  isOpen?: boolean;
  onExpand: () => void;
  isFailed?: boolean;
}

const MainInfo: React.FC<MainInfoProps> = ({ job, attempts = [], isOpen, onExpand, isFailed }) => {
  const jobStatus = getJobStatus(job);
  const isPartialSuccess = partialSuccessCheck(attempts);

  const statusIcon = () => {
    switch (true) {
      case jobStatus === JobStatus.cancelled:
        return <StatusIcon status="error" />;
      case jobStatus === JobStatus.running:
        return <StatusIcon status="loading" />;
      case jobStatus === JobStatus.succeeded:
        return <StatusIcon status="success" />;
      case isPartialSuccess:
        return <StatusIcon status="warning" />;
      case !isPartialSuccess && isFailed:
        return <StatusIcon status="error" />;
      default:
        return null;
    }
  };

  return (
    <Row
      className={classNames(styles.mainView, { [styles.failed]: isFailed, [styles.open]: isOpen })}
      onClick={onExpand}
    >
      <Cell className={styles.titleCell}>
        <div className={styles.statusIcon}>{statusIcon()}</div>
        <div className={styles.justification}>
          {isPartialSuccess ? (
            <FormattedMessage id="sources.partialSuccess" />
          ) : (
            <FormattedMessage id={`sources.${getJobStatus(job)}`} />
          )}
          {attempts.length && (
            <>
              {attempts.length > 1 && (
                <div className={styles.lastAttempt}>
                  <FormattedMessage id="sources.lastAttempt" />
                </div>
              )}
              <AttemptDetails attempt={attempts[attempts.length - 1]} configType={getJobConfig(job)} />
            </>
          )}
        </div>
      </Cell>
      <Cell className={styles.timestampCell}>
        <div>
          <FormattedTimeParts value={getJobCreatedAt(job) * 1000} hour="numeric" minute="2-digit">
            {(parts) => <span>{`${parts[0].value}:${parts[2].value}${parts[4].value} `}</span>}
          </FormattedTimeParts>
          <FormattedDateParts value={getJobCreatedAt(job) * 1000} month="2-digit" day="2-digit">
            {(parts) => <span>{`${parts[0].value}/${parts[2].value}`}</span>}
          </FormattedDateParts>
          {attempts.length > 1 && (
            <div className={styles.attemptCount}>
              <FormattedMessage id="sources.countAttempts" values={{ count: attempts.length }} />
            </div>
          )}
        </div>
        <FontAwesomeIcon className={styles.arrow} icon={faAngleDown} />
      </Cell>
    </Row>
  );
};

export default MainInfo;
