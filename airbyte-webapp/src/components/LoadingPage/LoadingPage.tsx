import React from "react";

import { FlexContainer } from "components/ui/Flex";

import styles from "./LoadingPage.module.scss";
import { ReactComponent as LogoAnimation } from "./logo-animation.svg";

export const LoadingPage: React.FC = () => (
  <FlexContainer alignItems="center" justifyContent="center" className={styles.loadingPage}>
    <LogoAnimation />
  </FlexContainer>
);
