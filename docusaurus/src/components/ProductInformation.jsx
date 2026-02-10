import React from "react";
import classNames from "classnames";

import styles from "./ProductInformation.module.css";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faCheck,
  faQuestionCircle,
  faXmark,
} from "@fortawesome/free-solid-svg-icons";

const Badge = ({ available, children, title }) => {
  return (
    <span
      className={classNames(styles.badge, { [styles.available]: available })}
      title={title}
    >
      <FontAwesomeIcon
        icon={available ? faCheck : faXmark}
        title={available ? "Available" : "Not available"}
      />
      <span>{children}</span>
    </span>
  );
};

/**
 * @type {React.FC<{ products: string }}
 */
export const ProductInformation = ({ products }) => {
  products = Object.fromEntries(
    products.split(",").map((f) => [f.trim(), true]),
  );

  const ossCommunity =
    products["oss-community"] || products["oss-*"] || products["all"];
  const ossEnterprise =
    products["oss-enterprise"] || products["oss-*"] || products["all"];
  const cloud = products["cloud"] || products["cloud-teams"] || products["all"];
  // cloud add-ons need to be specifically marked and are not part of the "all" shorthand
  const cloudPlus = products["cloud-plus"];
  const cloudTeams = products["cloud-teams"];
  const enterpriseFlex = products["enterprise-flex"];
  const embedded = products["embedded"];

  return (
    <div className={styles.badges}>
      <Badge available={ossCommunity} title="Formerly Self-Managed Community">
        Core
      </Badge>
      <Badge
        available={cloud && !cloudTeams && !enterpriseFlex}
        title="Formerly Cloud"
      >
        Standard
      </Badge>
      <Badge available={cloud && !cloudTeams && !enterpriseFlex || cloudPlus}>Plus</Badge>
      <Badge available={cloudPlus || cloud || cloudTeams} title="Formerly Cloud Teams">
        Pro
      </Badge>
      <Badge available={cloudPlus || cloud || cloudTeams || enterpriseFlex}>
        Enterprise Flex
      </Badge>
      <Badge available={ossEnterprise}>Self-Managed Enterprise</Badge>
      {embedded && <Badge available={true}>Embedded</Badge>}
      <a
        href="https://airbyte.com/product/features"
        target="_blank"
        className={styles.helpIcon}
      >
        <FontAwesomeIcon icon={faQuestionCircle} /> Compare
      </a>
    </div>
  );
};
