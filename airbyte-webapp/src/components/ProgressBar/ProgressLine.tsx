// Inspired by https://dev.to/ramonak/react-how-to-create-a-custom-progress-bar-component-in-5-minutes-2lcl

import classNames from "classnames";

import styles from "./ProgressLine.module.scss";

interface ProgressLineProps {
  color: string;
  percent: number;
}

export const ProgressLine: React.FC<ProgressLineProps> = ({ color, percent }) => {
  return (
    <div className={classNames(styles.lineOuter)}>
      <div style={{ width: `${percent}%`, backgroundColor: color }} className={classNames(styles.lineInner)} />
    </div>
  );
};
