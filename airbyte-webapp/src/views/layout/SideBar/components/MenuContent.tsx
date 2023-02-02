import { PropsWithChildren } from "react";

import { FlexContainer } from "components/ui/Flex";

import styles from "./MenuContent.module.scss";

export const MenuContent: React.FC<PropsWithChildren<unknown>> = ({ children }) => {
  return (
    <FlexContainer
      direction="column"
      gap="xs"
      alignItems="center"
      justifyContent="space-between"
      className={styles.menuContent}
    >
      {children}
    </FlexContainer>
  );
};
