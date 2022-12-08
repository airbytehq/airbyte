import classNames from "classnames";
import { FormattedMessage, FormattedNumber, useIntl } from "react-intl";

import { Text } from "components/ui/Text";
import { Tooltip } from "components/ui/Tooltip";

import { AttemptStreamStats } from "core/request/AirbyteClient";

import styles from "./StreamProgress.module.scss";

interface StreamProgressProps {
  stream: AttemptStreamStats;
}

const CircleProgress: React.FC<{ percent: number }> = ({ percent }) => {
  const svgClassName = classNames(styles.progress, {
    [styles.done]: percent >= 1,
  });

  return (
    <svg width="16" height="16" viewBox="0 0 20 20" className={svgClassName}>
      <circle r="10" cx="10" cy="10" className={styles.bg} />
      <circle
        className={styles.fg}
        r="5"
        cx="10"
        cy="10"
        fill="transparent"
        stroke-width="10"
        strokeDasharray={`calc(${percent * 100} * 31.4/100) 31.4`}
        transform="rotate(-90) translate(-20)"
      />
      <path
        className={styles.check}
        fillRule="evenodd"
        clipRule="evenodd"
        d="M 8.4594,12.86489 5.62443,10.02988 6.52491,9.1294 l 2.38473,2.38469 4.56543,-4.56543 0.9005,0.90047 -5.0157,5.01576 c -0.24866,0.2486 -0.65181,0.2486 -0.90047,0 z"
      />
    </svg>
  );
};

export const StreamProgress: React.FC<StreamProgressProps> = ({ stream }) => {
  const { formatNumber } = useIntl();
  const { recordsEmitted, estimatedRecords } = stream.stats;

  const progress = estimatedRecords ? (recordsEmitted ?? 0) / estimatedRecords : undefined;

  return (
    <Tooltip
      control={
        <span className={styles.stream}>
          <Text as="span" size="xs" className={styles.wrapper}>
            {stream.streamName} {progress !== undefined && <CircleProgress percent={progress} />}
          </Text>
        </span>
      }
    >
      <Text bold as="div" inverseColor>
        <FormattedMessage id="connection.progress.streamTooltipTitle" values={{ stream: stream.streamName }} />
      </Text>
      <dl className={styles.metrics}>
        <dt>
          <FormattedMessage id="connection.progress.progress" />
        </dt>
        <dd>
          {progress !== undefined ? (
            <FormattedNumber value={progress} style="percent" />
          ) : (
            <FormattedMessage id="connection.progress.unknown" />
          )}
        </dd>
        {(estimatedRecords || recordsEmitted) && (
          <>
            <dt>
              <FormattedMessage id="connection.progress.records" />
            </dt>
            <dd>
              {estimatedRecords ? (
                <FormattedMessage
                  id="connection.progress.streamRecordsWithEstimate"
                  values={{ estimated: formatNumber(estimatedRecords), current: formatNumber(recordsEmitted ?? 0) }}
                />
              ) : (
                <FormattedMessage
                  id="connection.progress.streamRecordsWithoutEstimate"
                  values={{ current: formatNumber(recordsEmitted ?? 0) }}
                />
              )}
            </dd>
          </>
        )}
      </dl>
    </Tooltip>
  );
};
