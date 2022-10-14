import styles from "./ConnectorTestingPanel.module.scss";
import { StreamSelector } from "./StreamSelector";

interface ConnectorTestingPanelProps {
  streams: string[];
  selectedStream: string;
  onStreamSelect: (stream: string) => void;
}

export const ConnectorTestingPanel: React.FC<ConnectorTestingPanelProps> = ({
  streams,
  selectedStream,
  onStreamSelect,
}) => {
  return (
    <div className={styles.container}>
      <StreamSelector streams={streams} selectedStream={selectedStream} onSelect={onStreamSelect} />
    </div>
  );
};
