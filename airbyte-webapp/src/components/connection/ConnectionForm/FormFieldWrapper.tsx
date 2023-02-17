import React from "react";

import { FlexContainer } from "components/ui/Flex";

import styles from "./FormFieldWrapper.module.scss";

export const FormFieldWrapper: React.FC = ({ children }) => {
  const [label, ...restControls] = React.Children.toArray(children);

  return (
    <FlexContainer alignItems="center">
      <div className={styles.leftFieldCol}>{label}</div>
      <div className={styles.rightFieldCol}>{restControls}</div>
    </FlexContainer>
  );
};
