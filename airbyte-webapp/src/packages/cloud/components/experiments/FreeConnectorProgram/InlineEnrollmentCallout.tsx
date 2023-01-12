import React, { PropsWithChildren } from "react";
import { FormattedMessage } from "react-intl";

import { Callout } from "components/ui/Callout";
import { Text } from "components/ui/Text";

import styles from "./InlineEnrollmentCallout.module.scss";

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
    <Callout variant="blue" className={styles.container}>
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
