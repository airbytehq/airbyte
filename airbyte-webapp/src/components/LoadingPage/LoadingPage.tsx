import React from "react";
import { useIntl } from "react-intl";

import { FlexContainer } from "components/ui/Flex";

import styles from "./LoadingPage.module.scss";
import logoAnimationUrl from "./logo-animation.svg";

export const LoadingPage: React.FC = () => {
  const { formatMessage } = useIntl();
  return (
    <FlexContainer alignItems="center" justifyContent="center" className={styles.loadingPage}>
      <img src={logoAnimationUrl} alt={formatMessage({ id: "ui.loading" })} />
    </FlexContainer>
  );
};
