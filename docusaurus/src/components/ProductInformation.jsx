import React from "react";
import classNames from "classnames";

import styles from "./ProductInformation.module.css";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCheck, faQuestionCircle, faXmark } from "@fortawesome/free-solid-svg-icons";

const Badge = ({ available, children }) => {
  return (
    <span className={classNames(styles.badge, { [styles.available]: available })}>
      <FontAwesomeIcon icon={available ? faCheck : faXmark} title={available ? "Available" : "Not available"} />
      <span>{children}</span>
    </span>
  );
};

/**
 * @type {React.FC<{ products: string }}
 */
export const ProductInformation = ({ products }) => {
  products = Object.fromEntries(products.split(",").map(f => [f.trim(), true]));

  const ossCommunity = products["oss-community"] || products["oss-*"] || products["all"];
  const ossEnterprise = products["oss-enterprise"] || products["oss-*"] || products["all"];
  const cloud = products["cloud"] || products["cloud-teams"] || products["all"];
  // cloud add-ons need to be specifically marked and are not part of the "all" shorthand
  const cloudTeams = products["cloud-teams"];
  const embedded = products["embedded"];

  return (
    <div className={styles.badges}>
      <Badge available={cloud}>Cloud {cloudTeams ? <span className={styles.withAddon}>with Teams add-on</span> : ""}</Badge>
      <Badge available={ossCommunity}>Self-Managed Community</Badge>
      <Badge available={ossEnterprise}>Self-Managed Enterprise</Badge>
      {embedded && <Badge available={true}>Embedded</Badge>}
      <a href="https://airbyte.com/product/features" target="_blank" className={styles.helpIcon}>
        <FontAwesomeIcon icon={faQuestionCircle} /> Compare
      </a>
    </div>
  );
}
