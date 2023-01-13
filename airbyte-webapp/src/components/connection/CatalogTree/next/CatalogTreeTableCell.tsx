import classNames from "classnames";
import React, { useCallback, useLayoutEffect, useState } from "react";
import { useWindowSize } from "react-use";

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

const TooltipText: React.FC<{ textNodes: Element[] }> = ({ textNodes }) => {
  if (!textNodes.length) {
    return null;
  }
  return <>{textNodes.map((t) => t.innerHTML).join(" | ")}</>;
};

export const CatalogTreeTableCell: React.FC<React.PropsWithChildren<CatalogTreeTableCellProps>> = ({
  size = "medium",
  withTooltip,
  className,
  children,
}) => {
  const [tooltipDisabled, setTooltipDisabled] = useState(false);
  const [textNodes, setTextNodes] = useState<Element[]>([]);

  const { width: windowWidth } = useWindowSize();

  const handleCell = useCallback(
    (cell: HTMLDivElement) => cell && setTextNodes(Array.from(cell.querySelectorAll(`[data-type="text"]`))),
    []
  );

  useLayoutEffect(() => {
    // need setTimeout so this runs after the DOM is finished rendering
    // otherwise the node width's aren't calculated correctly
    setTimeout(() => {
      // windowWidth is only here so this functionality changes based on window width
      if (textNodes.length && windowWidth) {
        const [scrollWidths, clientWidths] = textNodes.reduce(
          ([scrollWidths, clientWidths], textNode) => {
            if (textNode) {
              scrollWidths += textNode.scrollWidth;
              clientWidths += textNode.clientWidth;
            }
            return [scrollWidths, clientWidths];
          },
          [0, 0]
        );
        if (scrollWidths > clientWidths) {
          setTooltipDisabled(false);
        } else {
          setTooltipDisabled(true);
        }
      }
    }, 100);
  }, [textNodes, windowWidth]);

  return (
    <div ref={handleCell} className={classNames(styles.tableCell, className, sizeMap[size])}>
      {withTooltip ? (
        <Tooltip
          className={styles.noEllipsis}
          control={children}
          theme="light"
          placement="top-start"
          disabled={tooltipDisabled}
        >
          <TooltipText textNodes={textNodes} />
        </Tooltip>
      ) : (
        children
      )}
    </div>
  );
};
