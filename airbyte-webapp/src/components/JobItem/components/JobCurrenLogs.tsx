import React, { useState } from "react";
import { FormattedMessage } from "react-intl";

import { Attempt } from "core/resources/Job";
import AttemptDetails from "./AttemptDetails";
import DownloadButton from "./DownloadButton";
import Logs from "./Logs";
import Tabs from "./Tabs";
import CenteredDetails from "./CenteredDetails";

type IProps = {
  id: number | string;
  jobIsFailed?: boolean;
  attempts: {
    attempt: Attempt;
    logs: { logLines: string[] };
  }[];
  logs?: { logLines: string[] };
};

const JobCurrentLogs: React.FC<IProps> = ({
  id,
  jobIsFailed,
  attempts,
  logs,
}) => {
  const [attemptNumber, setAttemptNumber] = useState<number>(
    attempts.length ? attempts.length - 1 : 0
  );

  const data = attempts?.map((item, index) => ({
    id: index.toString(),
    status: item.attempt?.status,
    name: (
      <FormattedMessage
        id="sources.attemptNum"
        values={{ number: index + 1 }}
      />
    ),
  }));

  const logsText = attempts.length ? attempts[attemptNumber].logs : logs;
  const attemptId = attempts.length ? attempts[attemptNumber].attempt.id : "";

  return (
    <>
      {attempts.length > 1 ? (
        <Tabs
          activeStep={attemptNumber.toString()}
          onSelect={(at) => setAttemptNumber(parseInt(at))}
          data={data}
          isFailed={jobIsFailed}
        />
      ) : null}
      <CenteredDetails>
        {attempts.length > 1 && (
          <AttemptDetails attempt={attempts[attemptNumber].attempt} />
        )}
        <div>{`/tmp/workspace/${id}/${attemptId}/logs.log`}</div>

        <DownloadButton
          logs={logsText?.logLines || []}
          fileName={`logs-${id}-${attemptId}`}
        />
      </CenteredDetails>
      <Logs>
        {logsText?.logLines.map((item, key) => (
          <div key={`log-${id}-${key}`}>{item}</div>
        ))}
      </Logs>
    </>
  );
};

export default JobCurrentLogs;
