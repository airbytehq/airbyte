import styles from "./ConnectorTestingPanel.module.scss";
import { StreamSelector } from "./StreamSelector";
import { TestControls } from "./TestControls";

interface ConnectorTestingPanelProps {
  streams: Array<{ name: string; url: string }>;
  selectedStream: string;
  onStreamSelect: (stream: string) => void;
}

export const ConnectorTestingPanel: React.FC<ConnectorTestingPanelProps> = ({
  streams,
  selectedStream,
  onStreamSelect,
}) => {
  const selectedStreamUrl = streams.find((stream) => stream.name === selectedStream)?.url ?? "";

  return (
    <div className={styles.container}>
      <StreamSelector
        streamNames={streams.map((stream) => stream.name)}
        selectedStream={selectedStream}
        onSelect={onStreamSelect}
      />
      <TestControls
        url={selectedStreamUrl}
        onClickTest={() => {
          console.log("Test!");
        }}
      />
    </div>
  );
};
