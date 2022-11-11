import { faCaretDown, faCaretUp } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import * as React from "react";

import styles from "./SortIcon.module.scss";

interface SortIconProps {
  lowToLarge?: boolean;
  wasActive?: boolean;
}

const SortIcon: React.FC<SortIconProps> = ({ wasActive, lowToLarge }) => (
  <FontAwesomeIcon className={styles.sortIcon} icon={lowToLarge || !wasActive ? faCaretUp : faCaretDown} />
);

export default SortIcon;
