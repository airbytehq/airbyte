import React from "react";

import { Attempt, Logs, JobDebugInfoMeta } from "core/domain/job";
import DownloadButton from "./DownloadButton";
import DebugInfoButton from "./DebugInfoButton";
import LogsTable from "./Logs";
import AttemptDetails from "./AttemptDetails";
import styled from "styled-components";

const CenteredDetails = styled.div`
  text-align: center;
  padding-top: 9px;
  font-size: 12px;
  line-height: 28px;
  color: ${({ theme }) => theme.greyColor40};
  position: relative;
`;

const LogsDetails: React.FC<{
  id: number | string;
  path: string;
  currentAttempt?: Attempt | null;
  logs?: Logs;
  jobDebugInfo?: JobDebugInfoMeta;
}> = ({ path, logs, id, currentAttempt, jobDebugInfo }) => (
  <>
    {currentAttempt && <AttemptDetails attempt={currentAttempt} />}
    <CenteredDetails>
      <div>{path}</div>
      {logs?.logLines && (
        <DownloadButton logs={logs?.logLines ?? []} fileName={`logs-${id}`} />
      )}
      {jobDebugInfo && <DebugInfoButton jobDebugInfo={jobDebugInfo} />}
    </CenteredDetails>
    <LogsTable logsArray={logs?.logLines} />
  </>
);

export { LogsDetails };
