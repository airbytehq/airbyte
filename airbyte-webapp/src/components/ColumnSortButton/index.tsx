import React from "react";
import { FormattedMessage } from "react-intl";

import styles from "./ColumnSortButton.module.scss";
import SortIcon from "./SortIcon";

interface ColumnSortButtonProps {
  onClick: () => void;
  formattedMessageId: string;
  wasActive: boolean;
  lowToLarge: boolean;
}

export const ColumnSortButton: React.FC<ColumnSortButtonProps> = ({
  onClick,
  formattedMessageId,
  wasActive,
  lowToLarge,
}) => (
  <button className={styles.sortButton} onClick={onClick}>
    <FormattedMessage id={formattedMessageId} />
    <SortIcon wasActive={wasActive} lowToLarge={lowToLarge} />
  </button>
);
