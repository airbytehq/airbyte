import React, { useState } from "react";
import { FormattedMessage } from "react-intl";

import { Attempt } from "../../../core/resources/Job";
import AttemptDetails from "./AttemptDetails";
import DownloadButton from "./DownloadButton";
import Logs from "./Logs";
import Tabs from "./Tabs";
import CenteredDetails from "./CenteredDetails";

type IProps = {
  id: number;
  jobIsFailed?: boolean;
  attempts: {
    attempt: Attempt;
    logs: { logLines: string[] };
  }[];
};

const JobCurrentLogs: React.FC<IProps> = ({ id, jobIsFailed, attempts }) => {
  const [attemptNumber, setAttemptNumber] = useState<any>(
    attempts.length ? attempts.length - 1 : 0
  );

  const data = attempts.map((item, key: any) => ({
    id: key,
    status: item.attempt.status,
    name: (
      <FormattedMessage id="sources.attemptNum" values={{ number: key + 1 }} />
    )
  }));

  return (
    <>
      {attempts.length > 1 ? (
        <Tabs
          activeStep={attemptNumber}
          onSelect={setAttemptNumber}
          data={data}
          isFailed={jobIsFailed}
        />
      ) : null}
      <CenteredDetails>
        {attempts.length > 1 && (
          <AttemptDetails attempt={attempts[attemptNumber].attempt} />
        )}
        <div>{`/tmp/workspace/${id}/${attempts[attemptNumber].attempt.id}/logs.log`}</div>

        <DownloadButton
          logs={attempts[attemptNumber].logs.logLines}
          fileName={`logs-${id}-${attempts[attemptNumber].attempt.id}`}
        />
      </CenteredDetails>
      <Logs>
        {attempts[attemptNumber].logs.logLines.map((item, key) => (
          <div key={`log-${id}-${key}`}>{item}</div>
        ))}
      </Logs>
    </>
  );
};

export default JobCurrentLogs;
