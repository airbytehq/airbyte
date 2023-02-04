import classNames from "classnames";
import React, { useEffect, useRef, useState } from "react";
import { useInView } from "react-intersection-observer";

import { Tooltip } from "components/ui/Tooltip";

import styles from "./CatalogTreeTableCell.module.scss";

type Sizes = "xsmall" | "small" | "medium" | "large";

interface CatalogTreeTableCellProps {
  size?: Sizes;
  className?: string;
  withTooltip?: boolean;
  ellipsisContent?: boolean;
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
  ellipsisContent = false,
  withTooltip,
  className,
  children,
}) => {
  const [tooltipDisabled, setTooltipDisabled] = useState(true);
  const [windowWidth, setWindowWidth] = useState<number>(window.innerWidth);
  const cellContent = useRef<HTMLSpanElement | null>(null);

  const { inView, ref } = useInView();

  useEffect(() => {
    if (inView) {
      const onResize = () => {
        setWindowWidth(window.innerWidth);
      };
      window.addEventListener("resize", onResize);
      return () => {
        window.removeEventListener("resize", onResize);
      };
    }

    return undefined;
  }, [inView]);

  useEffect(() => {
    if (!cellContent.current || cellContent.current?.scrollWidth > cellContent.current?.clientWidth) {
      setTooltipDisabled(false);
    } else {
      setTooltipDisabled(true);
    }
  }, [windowWidth, inView]);

  return (
    <div className={classNames(styles.tableCell, className, sizeMap[size])}>
      {withTooltip ? (
        <Tooltip
          className={classNames(styles.noEllipsis, styles.fullWidthTooltip)}
          control={
            <span
              ref={(el) => {
                ref(el);
                cellContent.current = el;
              }}
              className={classNames({ [styles.ellipsis]: ellipsisContent })}
            >
              {children}
            </span>
          }
          placement="bottom-start"
          disabled={tooltipDisabled}
        >
          {cellContent?.current?.textContent}
        </Tooltip>
      ) : (
        children
      )}
    </div>
  );
};
