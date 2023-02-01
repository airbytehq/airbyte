import React from "react";

import { Heading } from "components/ui/Heading";

import styles from "./FormTitle.module.scss";

export const FormTitle: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => (
  <Heading as="h1" size="xl" className={styles.title}>
    {children}
  </Heading>
);
