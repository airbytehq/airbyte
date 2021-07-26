import React, { useState } from "react";
import { useResource, useSubscription } from "rest-hooks";
import { FormattedMessage } from "react-intl";

import JobResource from "core/resources/Job";
import AttemptDetails from "./AttemptDetails";
import DownloadButton from "./DownloadButton";
import Logs from "./Logs";
import Tabs from "./Tabs";
import CenteredDetails from "./CenteredDetails";
import Status from "core/statuses";

type IProps = {
  id: number | string;
  jobIsFailed?: boolean;
};

const JobLogs: React.FC<IProps> = ({ id, jobIsFailed }) => {
  const job = useResource(JobResource.detailShape(), { id });
  useSubscription(JobResource.detailShape(), { id });

  const [attemptNumber, setAttemptNumber] = useState<number>(
    job.attempts.length ? job.attempts.length - 1 : 0
  );

  if (!job.attempts.length) {
    return <Logs />;
  }

  const data = job.attempts.map((item, index) => ({
    id: index.toString(),
    status:
      item.status === Status.FAILED || item.status === Status.SUCCEEDED
        ? item.status
        : undefined,
    name: (
      <FormattedMessage
        id="sources.attemptNum"
        values={{ number: index + 1 }}
      />
    ),
  }));

  const hasLogs = !!job.logsByAttempt[attemptNumber]?.logLines?.length;
  return (
    <>
      {job.attempts.length > 1 ? (
        <Tabs
          activeStep={attemptNumber.toString()}
          onSelect={(at) => setAttemptNumber(parseInt(at))}
          data={data}
          isFailed={jobIsFailed}
        />
      ) : null}
      <CenteredDetails>
        {job.attempts.length > 1 && (
          <AttemptDetails attempt={job.attempts[attemptNumber]} />
        )}
        <div>{`/tmp/workspace/${id}/${job.attempts[attemptNumber].id}/logs.log.`}</div>
        {hasLogs ? (
          <DownloadButton
            logs={job.logsByAttempt[attemptNumber].logLines}
            fileName={`logs-${id}-${job.attempts[attemptNumber].id}`}
          />
        ) : null}
      </CenteredDetails>
      <Logs
        logsArray={
          hasLogs ? job.logsByAttempt[attemptNumber].logLines : undefined
        }
      />
    </>
  );
};

export default JobLogs;
