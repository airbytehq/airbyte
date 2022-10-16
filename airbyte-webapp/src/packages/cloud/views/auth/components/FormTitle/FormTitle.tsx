import React from "react";

import { Text } from "components/ui/Text";

import styles from "./FormTitle.module.scss";

export const FormTitle: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => (
  <Text as="h1" size="xl" className={styles.title}>
    {children}
  </Text>
);
