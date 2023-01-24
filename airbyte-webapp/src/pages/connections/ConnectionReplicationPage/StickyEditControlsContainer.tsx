import React from "react";

import { Card } from "components/ui/Card";

import styles from "./StickyEditControlsContainer.module.scss";

export const StickyEditControlsContainer: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => (
  <div className={styles.container}>
    <Card className={styles.halfCard} />
    {children}
  </div>
);
