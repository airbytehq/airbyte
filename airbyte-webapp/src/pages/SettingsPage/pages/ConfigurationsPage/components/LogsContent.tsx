import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { useAsyncFn } from "react-use";
import styled from "styled-components";

import { LoadingButton } from "components";

import { LogType } from "core/domain/logs/types";
import { useNotificationService } from "hooks/services/Notification";
import { useGetLogs } from "services/logs/LogsService";
import { downloadFile } from "utils/file";

const Content = styled.div`
  padding: 29px 0 27px;
  text-align: center;
`;

const LogsButton = styled(LoadingButton)`
  margin: 0 15px;
`;

const LogsContent: React.FC = () => {
  const { registerNotification } = useNotificationService();
  const { formatMessage } = useIntl();

  const fetchLogs = useGetLogs();

  const downloadLogs = async (logType: LogType) => {
    try {
      const file = await fetchLogs({ logType });
      const name = `${logType}-logs.txt`;
      downloadFile(file, name);
    } catch (e) {
      console.error(e);

      registerNotification({
        id: "admin.logs.error",
        title: formatMessage({ id: "admin.logs.error" }),
        isError: true,
      });
    }
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
