import { useMemo } from "react";
import { FormattedMessage } from "react-intl";

import { Text } from "components/ui/Text";

import { StreamReadLogsItem } from "core/request/ConnectorBuilderClient";

import styles from "./LogsDisplay.module.scss";
import { formatJson } from "./utils";

interface LogsDisplayProps {
  logs: StreamReadLogsItem[];
  onTitleClick: () => void;
}

export const LogsDisplay: React.FC<LogsDisplayProps> = ({ logs, onTitleClick }) => {
  const formattedLogs = useMemo(() => formatJson(logs), [logs]);

  return (
    <div className={styles.container}>
      <button className={styles.header} onClick={onTitleClick}>
        <Text size="sm" bold>
          <FormattedMessage id="connectorBuilder.connectorLogs" />
        </Text>
        <Text className={styles.numLogsDisplay} size="xs" bold>
          {logs.length}
        </Text>
      </button>
      <div className={styles.logsDisplay}>
        <pre>{formattedLogs}</pre>
      </div>
    </div>
  );
};
