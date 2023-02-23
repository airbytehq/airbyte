import React from "react";
import { FormattedMessage } from "react-intl";

import { Button } from "components/ui/Button";
import { Callout } from "components/ui/Callout";
import { FlexContainer, FlexItem } from "components/ui/Flex";
import { Heading } from "components/ui/Heading";
import { Text } from "components/ui/Text";

import { ReactComponent as ConnectorsBadges } from "./connectors-badges.svg";
import { useShowEnrollmentModal } from "./EnrollmentModal";
import { useFreeConnectorProgram } from "./hooks/useFreeConnectorProgram";
import styles from "./LargeEnrollmentCallout.module.scss";

export const LargeEnrollmentCallout: React.FC = () => {
  const { showEnrollmentModal } = useShowEnrollmentModal();
  const { userDidEnroll, enrollmentStatusQuery } = useFreeConnectorProgram();
  const { showEnrollmentUi } = enrollmentStatusQuery.data || {};

  if (userDidEnroll || !showEnrollmentUi) {
    return null;
  }

  return (
    <Callout variant="boldInfo" className={styles.container}>
      <FlexContainer direction="row" alignItems="center" className={styles.flexRow}>
        <FlexItem grow={false} alignSelf="center">
          <ConnectorsBadges />
        </FlexItem>
        <FlexContainer direction="column" gap="xs">
          <Heading size="sm" className={styles.title} as="h3" inverseColor>
            <FormattedMessage id="freeConnectorProgram.title" />
          </Heading>
          <Text size="sm" inverseColor>
            <FormattedMessage id="freeConnectorProgram.enroll.description" />
          </Text>
        </FlexContainer>
        <Button variant="dark" className={styles.enrollButton} onClick={showEnrollmentModal}>
          <FormattedMessage id="freeConnectorProgram.enrollNow" />
        </Button>
      </FlexContainer>
    </Callout>
  );
};
