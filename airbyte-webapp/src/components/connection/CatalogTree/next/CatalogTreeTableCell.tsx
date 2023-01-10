import classNames from "classnames";
import React from "react";

import styles from "./CatalogTreeTableCell.module.scss";

type Sizes = "xsmall" | "small" | "medium" | "large";

interface CatalogTreeTableCellProps {
  size?: Sizes;
  className?: string;
  withTooltip?: boolean;
}

// This lets us avoid the eslint complaint about unused styles
const sizeMap: Record<Sizes, string> = {
  xsmall: styles.xsmall,
  small: styles.small,
  medium: styles.medium,
  large: styles.large,
};

export const CatalogTreeTableCell: React.FC<React.PropsWithChildren<CatalogTreeTableCellProps>> = ({
  size = "medium",
  withTooltip,
  className,
  children,
}) => {
  const style = classNames(styles.tableCell, className, sizeMap[size], withTooltip);
  // if (withTooltip) {
  //   return (
  //     <div className={style}>
  //       <Tooltip className={style} control={children} theme="light" placement="top-start">
  //         {children}
  //       </Tooltip>
  //     </div>
  //   );
  // }
  return (
    <div className={style}>
      <div className={styles.tooltip}>{children}</div>
      {children}
    </div>
  );
};
