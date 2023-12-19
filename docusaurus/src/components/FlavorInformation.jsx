import React from "react";
import classNames from "classnames";

import styles from "./FlavorInformation.module.css";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCheckCircle, faQuestionCircle, faXmarkCircle } from "@fortawesome/free-regular-svg-icons";

const Badge = ({ available, children }) => {
  return (
    <span className={classNames(styles.badge, { [styles.available]: available })}>
      <FontAwesomeIcon size="md" icon={available ? faCheckCircle : faXmarkCircle} title={available ? "Available" : "Not available"} />
      <span>{children}</span>
    </span>
  );
};

/**
 * @type {React.FC<{ flavors: string }}
 */
export const FlavorInformation = ({ flavors }) => {
  flavors = Object.fromEntries(flavors.split(",").map(f => [f.trim(), true]));

  const ossCommunity = flavors["oss-community"] || flavors["oss-*"] || flavors["all"];
  const ossEnterprise = flavors["oss-enterprise"] || flavors["oss-*"] || flavors["all"];
  const cloud = flavors["cloud"] || flavors["cloud-teams"] || flavors["all"];
    // cloud add-ons need to be specifically marked and are not part of the "all" shorthand
  const cloudTeams = flavors["cloud-teams"];

  return (
    <div className={styles.badges}>
      <Badge available={cloud}>Cloud {cloudTeams ? <span className={styles.withAddon}>with Teams add-on</span> : ""}</Badge>
      <Badge available={ossCommunity}>Self-Managed Community (OSS)</Badge>
      <Badge available={ossEnterprise}>Self-Managed Enterprise</Badge>
      <a href="https://airbyte.com/product/features" target="_blank" className={styles.helpIcon}>
        <FontAwesomeIcon icon={faQuestionCircle} size="md" />
      </a>
    </div>
  );
}