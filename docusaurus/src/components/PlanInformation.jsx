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

  const isAll = parsed["all"];
  const free = isAll || parsed["free"];
  const individual = isAll || parsed["individual"];
  const team = isAll || parsed["team"];
  const custom = isAll || parsed["custom"];

  return (
    <div className={styles.badges}>
      <Badge available={free} title="Included in the Free plan">
        Free
      </Badge>
      <Badge available={individual} title="Included in the Individual plan">
        Individual
      </Badge>
      <Badge available={team} title="Included in the Team plan">
        Team
      </Badge>
      <Badge available={custom} title="Included in the Custom plan">
        Custom
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
