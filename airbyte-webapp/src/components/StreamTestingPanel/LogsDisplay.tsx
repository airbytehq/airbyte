import { FormattedMessage } from "react-intl";

import { Text } from "components/ui/Text";

import { StreamReadLogsItem } from "core/request/ConnectorBuilderClient";

import styles from "./LogsDisplay.module.scss";

interface LogsDisplayProps {
  logs: StreamReadLogsItem[];
}

export const LogsDisplay: React.FC<LogsDisplayProps> = ({ logs }) => {
  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <Text size="sm" bold>
          <FormattedMessage id="connectorBuilder.connectorLogs" />
        </Text>
        <Text className={styles.numLogsDisplay} size="xs" bold>
          {logs.length}
        </Text>
      </div>
      <div className={styles.logsDisplay}>
        <pre>{JSON.stringify(logs, null, 2)}</pre>
      </div>
    </div>
  );
};
