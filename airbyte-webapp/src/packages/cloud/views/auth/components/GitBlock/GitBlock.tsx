import { faGithub } from "@fortawesome/free-brands-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { FC } from "react";
import { FormattedMessage } from "react-intl";

import { useConfig } from "../../../../../../config";
import styles from "./GitBlock.module.scss";

export interface GitBlockProps {
  titleStyle?: React.CSSProperties;
  messageStyle?: React.CSSProperties;
}
export const GitBlock: FC<GitBlockProps> = ({ titleStyle, messageStyle }) => {
  const config = useConfig();
  return (
    <div className={styles.container}>
      <a className={styles.link} href={config.links.gitLink} target="_blank" rel="noreferrer">
        <div className={styles.content}>
          <FontAwesomeIcon icon={faGithub} className={styles.icon} />
          <div>
            <p className={styles.hostingText} style={titleStyle}>
              <FormattedMessage id="login.selfhosting" />
            </p>
            <p className={styles.deployText} style={messageStyle}>
              <FormattedMessage id="login.deployInfrastructure" />
            </p>
          </div>
        </div>
      </a>
    </div>
  );
};
