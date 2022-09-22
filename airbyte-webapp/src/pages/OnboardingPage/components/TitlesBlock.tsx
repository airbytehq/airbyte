import React from "react";

import { Text } from "components/base/Text";

import styles from "./TitlesBlock.module.scss";

interface TitlesBlockProps {
  title: React.ReactNode;
  children?: React.ReactNode;
  testId?: string;
}

const TitlesBlock: React.FC<TitlesBlockProps> = ({ title, children, testId }) => {
  return (
    <div className={styles.container}>
      <Text as="h1" size="xl" centered data-testid={testId}>
        {title}
      </Text>
      <Text as="p" centered className={styles.content}>
        {children}
      </Text>
    </div>
  );
};

export default TitlesBlock;
