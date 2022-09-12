import React from "react";

import styles from "./GroupControls.module.scss";

interface GroupControlsProps {
  title: React.ReactNode;
  name?: string;
}

const GroupControls: React.FC<GroupControlsProps> = ({ title, children, name }) => {
  return (
    <div className={styles.groupControlSection}>
      <div className={styles.groupTitle}>{title}</div>
      <div className={styles.formGroup} data-testid={name}>
        {children}
      </div>
    </div>
  );
};

export default GroupControls;
