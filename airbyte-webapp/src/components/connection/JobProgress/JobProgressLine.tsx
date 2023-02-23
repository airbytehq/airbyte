// Inspired by https://dev.to/ramonak/react-how-to-create-a-custom-progress-bar-component-in-5-minutes-2lcl

import classNames from "classnames";
import { useIntl } from "react-intl";

import styles from "./JobProgressLine.module.scss";

interface ProgressLineProps {
  type?: "default" | "warning";
  percent: number;
}

export const ProgressLine: React.FC<ProgressLineProps> = ({ type = "default", percent }) => {
  const { formatMessage } = useIntl();
  return (
    <div
      className={classNames(styles.lineOuter)}
      aria-label={formatMessage({ id: "connection.progress.percentage" }, { percent: Math.floor(percent * 100) })}
    >
      <div
        style={{ width: `${percent * 100}%` }}
        className={classNames(styles.lineInner, {
          [styles.default]: type === "default",
          [styles.warning]: type === "warning",
        })}
      />
    </div>
  );
};
