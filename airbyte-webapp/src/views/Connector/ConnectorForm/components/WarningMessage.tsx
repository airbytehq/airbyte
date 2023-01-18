import React from "react";
import { FormattedMessage } from "react-intl";

import { Callout } from "components/ui/Callout";
import { Text } from "components/ui/Text";

import { ReleaseStage } from "core/request/AirbyteClient";
import { links } from "utils/links";

import styles from "./WarningMessage.module.scss";

interface WarningMessageProps {
  stage: typeof ReleaseStage.alpha | typeof ReleaseStage.beta;
}

export const WarningMessage: React.FC<WarningMessageProps> = ({ stage }) => {
  return (
    <Callout className={styles.calloutContainer}>
      <Text size="sm">
        <FormattedMessage id={`connector.releaseStage.${stage}.description`} />{" "}
        <FormattedMessage
          id="connector.connectorsInDevelopment.docLink"
          values={{
            lnk: (node: React.ReactNode) => (
              <a className={styles.link} href={links.productReleaseStages} target="_blank" rel="noreferrer">
                {node}
              </a>
            ),
          }}
        />
      </Text>
    </Callout>
  );
};
