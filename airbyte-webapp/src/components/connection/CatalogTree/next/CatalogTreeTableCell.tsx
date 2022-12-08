import classNames from "classnames";
import React from "react";

import styles from "./CatalogTreeTableCell.module.scss";

type Sizes = "small" | "medium" | "large";

interface CatalogTreeTableCellProps {
  size?: Sizes;
}

// This lets us avoid the eslint complaint about unused styles
const sizeMap: Record<Sizes, string> = {
  small: styles.small,
  medium: styles.medium,
  large: styles.large,
};

export const CatalogTreeTableCell: React.FC<React.PropsWithChildren<CatalogTreeTableCellProps>> = ({
  size = "medium",
  children,
}) => {
  return <div className={classNames(styles.tableCell, sizeMap[size])}>{children}</div>;
};
