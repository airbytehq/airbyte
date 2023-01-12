import React, { PropsWithChildren } from "react";
import { FormattedMessage } from "react-intl";

import { Callout } from "components/ui/Callout";
import { Text } from "components/ui/Text";

import { useShowEnrollmentModal } from "./EnrollmentModal";
import styles from "./InlineEnrollmentCallout.module.scss";

export const EnrollLink: React.FC<PropsWithChildren<unknown>> = ({ children }) => {
  const { showEnrollmentModal } = useShowEnrollmentModal();

  return (
    <button onClick={showEnrollmentModal} className={styles.enrollLink}>
      {children}
    </button>
  );
};
export const InlineEnrollmentCallout: React.FC = () => {
  // todo: turn this on so I can use the service instead of hardcoding!
  // const isFreeConnectorProgramEnabled = useExperiment("workspace.freeConnectorsProgram.visible", false);
  const isFreeConnectorProgramEnabled = true;
  // todo: implement actual call once merged with issue #4006
  // for now, we'll just default to false for enrolled
  const enrolledInFreeConnectorProgram = false;

  if (!isFreeConnectorProgramEnabled || enrolledInFreeConnectorProgram) {
    return null;
  }

  return (
    <Callout variant="info" className={styles.container}>
      <Text size="sm">
        <FormattedMessage
          id="freeConnectorProgram.youCanEnroll"
          values={{
            enrollLink: (content: React.ReactNode) => <EnrollLink>{content}</EnrollLink>,
            freeText: (content: React.ReactNode) => (
              <Text as="span" size="sm" bold className={styles.freeText}>
                {content}
              </Text>
            ),
          }}
        />
      </Text>
    </Callout>
  );
};
