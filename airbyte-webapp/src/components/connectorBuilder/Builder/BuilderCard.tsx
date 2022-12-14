import React from "react";

import { Card } from "components/ui/Card";

import styles from "./BuilderCard.module.scss";

export const BuilderCard: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => {
  return <Card className={styles.card}>{children}</Card>;
};
