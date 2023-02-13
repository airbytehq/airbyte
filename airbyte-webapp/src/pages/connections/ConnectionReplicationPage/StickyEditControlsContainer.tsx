import React from "react";

import styles from "./StickyEditControlsContainer.module.scss";

export const StickyEditControlsContainer: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => (
  <div className={styles.container}>{children}</div>
);
