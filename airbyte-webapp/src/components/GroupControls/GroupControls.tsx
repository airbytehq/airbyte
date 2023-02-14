import classNames from "classnames";
import React from "react";

import styles from "./GroupControls.module.scss";

interface GroupControlsProps {
  label: React.ReactNode;
  control?: React.ReactNode;
  controlClassName?: string;
  name?: string;
}

const GroupControls: React.FC<React.PropsWithChildren<GroupControlsProps>> = ({
  label,
  control,
  children,
  name,
  controlClassName,
}) => {
  return (
    // This outer div is necessary for .content > :first-child padding to be properly applied in the case of nested GroupControls
    <div>
      <div className={styles.container}>
        <div className={styles.title}>
          <div className={styles.label}>{label}</div>
          <div className={classNames(styles.control, controlClassName)}>{control}</div>
        </div>
        <div className={styles.content} data-testid={name}>
          {children}
        </div>
      </div>
    </div>
  );
};

export default GroupControls;
