import React from "react";

import { Heading } from "components/ui/Heading";

import styles from "./BuilderConfigView.module.scss";

interface BuilderConfigViewProps {
  heading: string;
}

export const BuilderConfigView: React.FC<React.PropsWithChildren<BuilderConfigViewProps>> = ({ children, heading }) => {
  return (
    <div className={styles.container}>
      <Heading className={styles.heading} as="h1">
        {heading}
      </Heading>
      {children}
    </div>
  );
};
