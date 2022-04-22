import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import { clamp } from "lodash";
import { useLocation } from "react-router-dom";

import Status from "core/statuses";
import { useGetJob, useGetDebugInfoJob } from "services/job/JobService";
import { Attempt } from "core/domain/job/Job";

import { parseAttemptLink } from "../attemptLinkUtils";
import Logs from "./Logs";
import Tabs from "./Tabs";
import { LogsDetails } from "./LogsDetails";

type IProps = {
  id: number | string;
  jobIsFailed?: boolean;
};

const isPartialSuccess = (attempt: Attempt) => {
  return !!attempt.failureSummary?.partialSuccess;
};

const JobLogs: React.FC<IProps> = ({ id, jobIsFailed }) => {
  const job = useGetJob(id);
  const debugInfo = useGetDebugInfoJob(id);

  const { hash } = useLocation();
  const [attemptNumber, setAttemptNumber] = useState<number>(() => {
    // If the link lead directly to an attempt use this attempt as the starting one
    // otherwise use the latest attempt
    const { attemptId, jobId } = parseAttemptLink(hash);
    if (jobId === String(id) && attemptId) {
      return clamp(parseInt(attemptId), 0, job.attempts.length - 1);
    }

    return job.attempts.length ? job.attempts.length - 1 : 0;
  });

  if (!job.attempts.length) {
    return <Logs />;
  }

  const currentAttempt = job.attempts[attemptNumber].attempt;
  const logs = job.attempts[attemptNumber]?.logs;
  const path = ["/tmp/workspace", id, currentAttempt.id, "logs.log"].join("/");

  const attemptsTabs = job.attempts.map((item, index) => ({
    id: index.toString(),
    isPartialSuccess: isPartialSuccess(item.attempt),
    status:
      item.attempt.status === Status.FAILED || item.attempt.status === Status.SUCCEEDED
        ? item.attempt.status
        : undefined,
    name: <FormattedMessage id="sources.attemptNum" values={{ number: index + 1 }} />,
  }));

  return (
    <>
      {job.attempts.length > 1 ? (
        <Tabs
          activeStep={attemptNumber.toString()}
          onSelect={(at) => setAttemptNumber(parseInt(at))}
          data={attemptsTabs}
          isFailed={jobIsFailed}
        />
      ) : null}
      <LogsDetails
        id={job.job.id}
        path={path}
        currentAttempt={job.attempts.length > 1 ? currentAttempt : null}
        logs={logs}
        jobDebugInfo={debugInfo.job}
      />
    </>
  );
};

export default JobLogs;
