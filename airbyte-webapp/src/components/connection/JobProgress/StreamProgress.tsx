import { FormattedNumber } from "react-intl";

import { Text } from "components/ui/Text";
import { Tooltip } from "components/ui/Tooltip";

import { AttemptStreamStats } from "core/request/AirbyteClient";

import styles from "./StreamProgress.module.scss";

interface StreamProgressProps {
  stream: AttemptStreamStats;
}

const CircleProgress: React.FC<{ percent: number }> = ({ percent }) => {
  return (
    <svg width="16" height="16" viewBox="0 0 20 20" className={styles.progress}>
      <circle r="10" cx="10" cy="10" fill="white" />
      <circle
        r="5"
        cx="10"
        cy="10"
        fill="transparent"
        stroke="#615eff"
        stroke-width="10"
        strokeDasharray={`calc(${percent * 100} * 31.4/100) 31.4`}
        transform="rotate(-90) translate(-20)"
      />
    </svg>
  );
};

// TODO: progress for stream
export const StreamProgress: React.FC<StreamProgressProps> = ({ stream }) => {
  const { recordsEmitted, estimatedRecords } = stream.stats;

  const progress = estimatedRecords ? (recordsEmitted ?? 0) / estimatedRecords : undefined;

  return (
    <Tooltip
      control={
        <span className={styles.stream}>
          <Text as="span" size="xs" className={styles.wrapper}>
            {/* {recordsEmitted && estimatedRecords && <CircleProgress percent={recordsEmitted / estimatedRecords} />} */}
            {stream.streamName} {progress !== undefined && <CircleProgress percent={progress} />}
          </Text>
        </span>
      }
    >
      <strong>Stream {stream.streamName}</strong>
      {recordsEmitted && estimatedRecords && (
        <FormattedNumber value={recordsEmitted / estimatedRecords} style="percent" />
      )}
    </Tooltip>
  );
};
