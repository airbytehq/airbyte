import React, { useState } from "react";
import { FormattedMessage } from "react-intl";

import Status from "core/statuses";
import { useGetJob } from "services/job/JobService";

import Logs from "./Logs";
import Tabs from "./Tabs";
import { LogsDetails } from "./LogsDetails";

type IProps = {
  id: number | string;
  jobIsFailed?: boolean;
};

const JobLogs: React.FC<IProps> = ({ id, jobIsFailed }) => {
  const job = useGetJob(id);

  const [attemptNumber, setAttemptNumber] = useState<number>(
    job.attempts.length ? job.attempts.length - 1 : 0
  );

  if (!job.attempts.length) {
    return <Logs />;
  }

  const currentAttempt = job.attempts[attemptNumber].attempt;
  const logs = job.attempts[attemptNumber]?.logs;
  const path = ["/tmp/workspace", id, currentAttempt.id, "logs.log"].join("/");

  const attemptsTabs = job.attempts.map((item, index) => ({
    id: index.toString(),
    status:
      item.attempt.status === Status.FAILED ||
      item.attempt.status === Status.SUCCEEDED
        ? item.attempt.status
        : undefined,
    name: (
      <FormattedMessage
        id="sources.attemptNum"
        values={{ number: index + 1 }}
      />
    ),
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
      />
    </>
  );
};

export default JobLogs;
