import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { useAsyncFn } from "react-use";
import styled from "styled-components";

import { Button } from "components/ui/Button";
import { ToastType } from "components/ui/Toast";

import { LogType } from "core/domain/logs/types";
import { useNotificationService } from "hooks/services/Notification";
import { useGetLogs } from "services/logs/LogsService";
import { downloadFile } from "utils/file";

import styles from "./LogsContainer.module.scss";

const Content = styled.div`
  padding: 29px 0 27px;
  text-align: center;
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
        text: formatMessage({ id: "admin.logs.error" }),
        type: ToastType.ERROR,
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
      <Button className={styles.logsButton} onClick={downloadServerLogs} isLoading={serverLogsLoading}>
        <FormattedMessage id="admin.downloadServerLogs" />
      </Button>
      <Button className={styles.logsButton} onClick={downloadSchedulerLogs} isLoading={schedulerLogsLoading}>
        <FormattedMessage id="admin.downloadSchedulerLogs" />
      </Button>
    </Content>
  );
};

export default LogsContent;
