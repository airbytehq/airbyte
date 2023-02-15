import classNames from "classnames";
import React, { useEffect, useRef, useState } from "react";
import { useInView } from "react-intersection-observer";
import { debounceTime, fromEvent } from "rxjs";

import { Tooltip } from "components/ui/Tooltip";

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
  const [tooltipDisabled, setTooltipDisabled] = useState(true);
  const cellContent = useRef<HTMLSpanElement | null>(null);

  const { inView, ref: inViewRef } = useInView({ delay: 500 });

  useEffect(() => {
    if (!inView || !withTooltip) {
      // Only handle resize events on the window for this cell (to determine if the tooltip)
      // needs to be shown if the cell is actually in view
      return;
    }

    // Calculate based on any potentially truncated `<Text>` element inside this cell, whether
    // the tooltip should show.
    const calculateTooltipVisible = () => {
      const hasEllipsisedElement = Array.from(cellContent.current?.querySelectorAll(`[data-type="text"]`) ?? []).some(
        (el) => el.scrollWidth > el.clientWidth
      );
      setTooltipDisabled(!hasEllipsisedElement);
    };

    // Recalculate if tooltips should be visible for this cell if the (debounced) window size changes
    const subscription = fromEvent(window, "resize", { passive: false })
      // Debounce, since the resize event fires constantly while a user's still resizing the window
      .pipe(debounceTime(500))
      .subscribe(() => {
        calculateTooltipVisible();
      });

    calculateTooltipVisible();

    return () => {
      subscription.unsubscribe();
    };
  }, [inView, withTooltip]);

  return (
    <div className={classNames(styles.tableCell, className, sizeMap[size])}>
      {withTooltip ? (
        <Tooltip
          className={classNames(styles.noEllipsis, styles.fullWidthTooltip)}
          control={
            <span
              ref={(el) => {
                inViewRef(el);
                cellContent.current = el;
              }}
            >
              {children}
            </span>
          }
          placement="bottom-start"
          disabled={tooltipDisabled}
        >
          {cellContent.current?.textContent}
        </Tooltip>
      ) : (
        children
      )}
    </div>
  );
};
