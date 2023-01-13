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
