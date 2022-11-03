import { faCaretDown, faCaretUp } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { PropsWithChildren } from "react";

import styles from "./SortableTableHeader.module.scss";

interface SortableTableHeaderProps {
  onClick: () => void;
  isActive: boolean;
  isAscending: boolean;
}

export const SortableTableHeader: React.FC<PropsWithChildren<SortableTableHeaderProps>> = ({
  onClick,
  isActive,
  isAscending,
  children,
}) => (
  <button className={styles.sortButton} onClick={onClick}>
    {children}
    <FontAwesomeIcon className={styles.sortIcon} icon={isAscending || !isActive ? faCaretUp : faCaretDown} />
  </button>
);
