import classNames from "classnames";

import styles from "./Indicator.module.scss";

export interface IndicatorProps {
  /**
   * Set to true to render an invisible indicator so reserve the space in the UI
   */
  hidden?: boolean;
  className?: string;
}

export const Indicator: React.FC<IndicatorProps> = ({ hidden, className }) => (
  <div className={classNames(className, styles.indicator, { [styles.hidden]: hidden })} />
);
