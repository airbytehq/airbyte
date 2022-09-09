import React from "react";

import styles from "./GroupControls.module.scss";

interface GroupControlsProps {
  title: React.ReactNode;
  name?: string;
}

const GroupControls: React.FC<GroupControlsProps> = ({ title, children, name }) => {
  return (
    <div className={styles.formGroup} data-testid={name}>
      <div className={styles.groupTitle}>{title}</div>
      {children}
    </div>
  );
};

export default GroupControls;
