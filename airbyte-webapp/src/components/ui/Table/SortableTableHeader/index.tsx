import { faCaretDown, faCaretUp } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { PropsWithChildren } from "react";

import styles from "./SortableTableHeader.module.scss";

interface SortableTableHeaderProps {
  onClick: () => void;
  wasActive: boolean;
  lowToLarge: boolean;
}

export const SortableTableHeader: React.FC<PropsWithChildren<SortableTableHeaderProps>> = ({
  onClick,
  wasActive,
  lowToLarge,
  children,
}) => (
  <button className={styles.sortButton} onClick={onClick}>
    {children}
    <FontAwesomeIcon className={styles.sortIcon} icon={lowToLarge || !wasActive ? faCaretUp : faCaretDown} />
  </button>
);
