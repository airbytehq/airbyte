import React from "react";
import classNames from "classnames";

import styles from "./PlanInformation.module.css";
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
 * @type {React.FC<{ plans: string }>}
 */
export const PlanInformation = ({ plans }) => {
  const parsed = Object.fromEntries(
    plans.split(",").map((p) => [p.trim(), true]),
  );

  // Free is independent of growth/pro/enterprise
  const free = parsed["free"];

  // Cascading logic: growth implies pro and enterprise; pro implies enterprise
  const growth = parsed["growth"];
  const pro = parsed["pro"] || growth;
  const enterprise = parsed["enterprise"] || pro;

  return (
    <div className={styles.badges}>
      <Badge available={free} title="Included in the Free plan">
        Free
      </Badge>
      <Badge available={growth} title="Included in the Growth plan and above">
        Growth
      </Badge>
      <Badge available={pro} title="Included in the Pro plan and above">
        Pro
      </Badge>
      <Badge available={enterprise} title="Included in the Enterprise plan">
        Enterprise
      </Badge>
      <a
        href="https://airbyte.com/product/ai-agents"
        target="_blank"
        className={styles.helpIcon}
      >
        <FontAwesomeIcon icon={faQuestionCircle} /> Compare plans
      </a>
    </div>
  );
};
