import { AttemptStreamStats } from "core/request/AirbyteClient";

import styles from "./StreamProgress.module.scss";

interface StreamProgressProps {
  stream: AttemptStreamStats;
}

export const StreamProgress: React.FC<StreamProgressProps> = ({ stream }) => {
  return <span className={styles.stream}>{stream.streamName}</span>;
};
