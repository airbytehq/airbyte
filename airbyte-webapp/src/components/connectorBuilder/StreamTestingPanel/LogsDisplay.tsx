import { useMemo } from "react";
import { FormattedMessage } from "react-intl";

import { NumberBadge } from "components/ui/NumberBadge";
import { Text } from "components/ui/Text";

import { StreamReadLogsItem } from "core/request/ConnectorBuilderClient";

import styles from "./LogsDisplay.module.scss";
import { formatJson } from "../utils";

interface LogsDisplayProps {
  logs: StreamReadLogsItem[];
  error?: string;
  onTitleClick: () => void;
}

export const LogsDisplay: React.FC<LogsDisplayProps> = ({ logs, error, onTitleClick }) => {
  const formattedLogs = useMemo(() => formatJson(logs), [logs]);

  return (
    <div className={styles.container}>
      <button className={styles.header} onClick={onTitleClick}>
        <Text size="sm" bold>
          <FormattedMessage id="connectorBuilder.connectorLogs" />
        </Text>
        {error !== undefined && <NumberBadge value={1} color="red" />}
      </button>
      <div className={styles.logsDisplay}>
        {error !== undefined ? <Text className={styles.error}>{error}</Text> : <pre>{formattedLogs}</pre>}
      </div>
    </div>
  );
};
