import React from "react";

import styles from "./GroupControls.module.scss";

interface GroupControlsProps {
  title: React.ReactNode;
  name?: string;
}

const GroupControls: React.FC<React.PropsWithChildren<GroupControlsProps>> = ({ title, children, name }) => {
  return (
    // This outer div is necessary for .content > :first-child padding to be properly applied in the case of nested GroupControls
    <div>
      <div className={styles.container}>
        <div className={styles.title}>{title}</div>
        <div className={styles.content} data-testid={name}>
          {children}
        </div>
      </div>
    </div>
  );
};

export default GroupControls;
