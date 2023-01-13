import React, { PropsWithChildren } from "react";
import { FormattedMessage } from "react-intl";

import { Button } from "components/ui/Button";
import { Callout } from "components/ui/Callout";
import { FlexContainer } from "components/ui/Flex";
import { Heading } from "components/ui/Heading";
import { Text } from "components/ui/Text";

import { ReactComponent as ConnectorsBadges } from "./connectors-badges.svg";
import styles from "./LargeEnrollmentCallout.module.scss";

export const EnrollLink: React.FC<PropsWithChildren<unknown>> = ({ children }) => {
  const onEnrollClick = () => {
    return null;
  };

  return (
    <span
      role="button"
      onClick={() => onEnrollClick()}
      onKeyDown={(e) => e.keyCode === 13 && onEnrollClick()}
      tabIndex={0}
      className={styles.enrollLink}
    >
      {children}
    </span>
  );
};
export const LargeEnrollmentCallout: React.FC = () => {
  return (
    <Callout variant="blueBold" className={styles.container}>
      <FlexContainer direction="row" justifyContent="space-between" alignItems="center" className={styles.flexRow}>
        <FlexContainer direction="column" gap="xs" className={styles.textContainer}>
          <ConnectorsBadges />
          <Heading size="sm" className={styles.title} as="h3">
            <FormattedMessage id="freeConnectorProgram.title" />
          </Heading>
          <Text size="sm">
            <FormattedMessage id="freeConnectorProgram.enroll.description" />
          </Text>
        </FlexContainer>
        <Button variant="dark">
          <FormattedMessage id="freeConnectorProgram.enrollNow" />
        </Button>
      </FlexContainer>
    </Callout>
  );
};
