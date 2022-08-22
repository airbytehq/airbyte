import { clamp } from "lodash";
import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import { useLocation } from "react-router-dom";

import { JobsWithJobs } from "pages/ConnectionPage/pages/ConnectionItemPage/components/JobsList";
import { useGetDebugInfoJob } from "services/job/JobService";

import { AttemptRead, AttemptStatus, SynchronousJobRead } from "../../../core/request/AirbyteClient";
import { parseAttemptLink } from "../attemptLinkUtils";
import Logs from "./Logs";
import { LogsDetails } from "./LogsDetails";
import Tabs, { TabsData } from "./Tabs";

interface JobLogsProps {
  jobIsFailed?: boolean;
  job: SynchronousJobRead | JobsWithJobs;
}

const isPartialSuccess = (attempt: AttemptRead) => {
  return !!attempt.failureSummary?.partialSuccess;
};

const jobIsSynchronousJobRead = (job: SynchronousJobRead | JobsWithJobs): job is SynchronousJobRead => {
  return !!(job as SynchronousJobRead)?.logs?.logLines;
};

const JobLogs: React.FC<JobLogsProps> = ({ jobIsFailed, job }) => {
  const isSynchronousJobRead = jobIsSynchronousJobRead(job);

  const id: number | string = (job as JobsWithJobs).job?.id ?? (job as SynchronousJobRead).id;

  const debugInfo = useGetDebugInfoJob(id, typeof id === "number", true);

  const { hash } = useLocation();
  const [attemptNumber, setAttemptNumber] = useState<number>(() => {
    // If the link lead directly to an attempt use this attempt as the starting one
    // otherwise use the latest attempt
    if (!isSynchronousJobRead && job.attempts) {
      const { attemptId, jobId } = parseAttemptLink(hash);
      if (!isNaN(Number(jobId)) && Number(jobId) === job.job.id && attemptId) {
        return clamp(parseInt(attemptId), 0, job.attempts.length - 1);
      }

      return job.attempts.length ? job.attempts.length - 1 : 0;
    }

    return 0;
  });

  if (isSynchronousJobRead) {
    return <Logs logsArray={debugInfo?.attempts[attemptNumber]?.logs.logLines ?? job.logs?.logLines} />;
  }

  const currentAttempt = job.attempts?.[attemptNumber];
  const path = ["/tmp/workspace", job.job.id, currentAttempt?.id, "logs.log"].join("/");

  const attemptsTabs: TabsData[] =
    job.attempts?.map((item, index) => ({
      id: index.toString(),
      isPartialSuccess: isPartialSuccess(item),
      status: item.status === AttemptStatus.failed || item.status === AttemptStatus.succeeded ? item.status : undefined,
      name: <FormattedMessage id="sources.attemptNum" values={{ number: index + 1 }} />,
    })) ?? [];

  const attempts = job.attempts?.length ?? 0;

  return (
    <>
      {attempts > 1 ? (
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
        currentAttempt={currentAttempt}
        jobDebugInfo={debugInfo}
        showAttemptStats={attempts > 1}
        logs={debugInfo?.attempts[attemptNumber]?.logs.logLines}
      />
    </>
  );
};

export default JobLogs;
