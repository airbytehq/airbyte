import React from "react";

import { Text } from "components/base/Text";

import styles from "./FormTitle.module.scss";

export const FormTitle: React.FC = ({ children }) => (
  <Text as="h1" size="xl" className={styles.title}>
    {children}
  </Text>
);
