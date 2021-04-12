import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { useFetcher } from "rest-hooks";

import LogsResource from "core/resources/Logs";
import { useAsyncFn } from "react-use";
import LoadingButton from "components/Button/LoadingButton";

const Content = styled.div`
  padding: 29px 0 27px;
  text-align: center;
`;

const LogsButton = styled(LoadingButton)`
  margin: 0 15px;
`;

const LogsContent: React.FC = () => {
  const fetchLogs = useFetcher(LogsResource.detailShape());

  const downloadLogs = async (logType: string) => {
    const { file } = await fetchLogs({ logType });

    const element = document.createElement("a");
    element.href = URL.createObjectURL(file);
    element.download = `${logType}-logs.txt`;
    document.body.appendChild(element); // Required for this to work in FireFox
    element.click();
    document.body.removeChild(element);
  };

  const [
    { loading: serverLogsLoading },
    downloadServerLogs,
  ] = useAsyncFn(async () => {
    await downloadLogs("server");
  }, [downloadLogs]);

  const [
    { loading: schedulerLogsLoading },
    downloadSchedulerLogs,
  ] = useAsyncFn(async () => {
    await downloadLogs("scheduler");
  }, [downloadLogs]);

  return (
    <Content>
      <LogsButton onClick={downloadServerLogs} isLoading={serverLogsLoading}>
        <FormattedMessage id="admin.downloadServerLogs" />
      </LogsButton>
      <LogsButton
        onClick={downloadSchedulerLogs}
        isLoading={schedulerLogsLoading}
      >
        <FormattedMessage id="admin.downloadSchedulerLogs" />
      </LogsButton>
    </Content>
  );
};

export default LogsContent;
