import { faCaretDown, faCaretUp } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import * as React from "react";

import styles from "./SortIcon.module.scss";

interface IProps {
  lowToLarge?: boolean;
  wasActive?: boolean;
}

const SortIcon: React.FC<IProps> = ({ wasActive, lowToLarge }) => (
  <FontAwesomeIcon className={styles.sortIcon} icon={lowToLarge || !wasActive ? faCaretUp : faCaretDown} />
);

export default SortIcon;
