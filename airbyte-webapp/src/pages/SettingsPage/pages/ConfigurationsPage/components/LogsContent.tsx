import React from "react";
import { FormattedMessage } from "react-intl";
import { useAsyncFn } from "react-use";
import styled from "styled-components";

import { LoadingButton } from "components";

import { useGetLogs } from "services/logs/LogsService";

import { LogType } from "../../../../../core/domain/logs/types";

const Content = styled.div`
  padding: 29px 0 27px;
  text-align: center;
`;

const LogsButton = styled(LoadingButton)`
  margin: 0 15px;
`;

const downloadFile = (file: Blob, name: string) => {
  const element = document.createElement("a");
  element.href = URL.createObjectURL(file);
  element.download = name;
  document.body.appendChild(element); // Required for this to work in FireFox
  element.click();
  document.body.removeChild(element);
};

const LogsContent: React.FC = () => {
  const fetchLogs = useGetLogs();

  const downloadLogs = async (logType: LogType) => {
    const file = await fetchLogs({ logType });
    const name = `${logType}-logs.txt`;
    downloadFile(file, name);
  };

  // TODO: get rid of useAsyncFn and use react-query
  const [{ loading: serverLogsLoading }, downloadServerLogs] = useAsyncFn(
    async () => await downloadLogs(LogType.Server),
    [downloadLogs]
  );

  const [{ loading: schedulerLogsLoading }, downloadSchedulerLogs] = useAsyncFn(
    async () => await downloadLogs(LogType.Scheduler),
    [downloadLogs]
  );

  return (
    <Content>
      <LogsButton onClick={downloadServerLogs} isLoading={serverLogsLoading}>
        <FormattedMessage id="admin.downloadServerLogs" />
      </LogsButton>
      <LogsButton onClick={downloadSchedulerLogs} isLoading={schedulerLogsLoading}>
        <FormattedMessage id="admin.downloadSchedulerLogs" />
      </LogsButton>
    </Content>
  );
};

export default LogsContent;
