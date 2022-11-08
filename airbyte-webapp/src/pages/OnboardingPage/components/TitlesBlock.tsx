import React from "react";

import { Heading } from "components/ui/Heading";
import { Text } from "components/ui/Text";

import styles from "./TitlesBlock.module.scss";

interface TitlesBlockProps {
  title: React.ReactNode;
  children?: React.ReactNode;
  testId?: string;
}

const TitlesBlock: React.FC<TitlesBlockProps> = ({ title, children, testId }) => {
  return (
    <div className={styles.container}>
      <Heading as="h1" size="lg" centered data-testid={testId}>
        {title}
      </Heading>
      <Text centered className={styles.content}>
        {children}
      </Text>
    </div>
  );
};

export default TitlesBlock;
