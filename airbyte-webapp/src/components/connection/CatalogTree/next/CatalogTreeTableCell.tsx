import classNames from "classnames";
import React, { useCallback, useEffect, useRef, useState } from "react";
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
  const text = textNodes.map((t) => decodeURIComponent(t.innerHTML)).join(" | ");
  // This is not a safe use, and need to be removed still.
  // https://github.com/airbytehq/airbyte/issues/22196
  // eslint-disable-next-line react/no-danger
  return <div dangerouslySetInnerHTML={{ __html: text }} />;
};

export const CatalogTreeTableCell: React.FC<React.PropsWithChildren<CatalogTreeTableCellProps>> = ({
  size = "medium",
  withTooltip,
  className,
  children,
}) => {
  const [tooltipDisabled, setTooltipDisabled] = useState(true);
  const [textNodes, setTextNodes] = useState<Element[]>([]);
  const cell = useRef<HTMLDivElement | null>(null);

  const { width: windowWidth } = useWindowSize();

  const getTextNodes = useCallback(() => {
    if (withTooltip && cell.current) {
      setTextNodes(Array.from(cell.current.querySelectorAll(`[data-type="text"]`)));
    }
  }, [withTooltip]);

  useEffect(() => {
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
  }, [textNodes, windowWidth]);

  return (
    <div ref={cell} className={classNames(styles.tableCell, className, sizeMap[size])} onMouseEnter={getTextNodes}>
      {withTooltip ? (
        <Tooltip
          className={classNames(styles.noEllipsis, styles.fullWidthTooltip)}
          control={children}
          placement="bottom-start"
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
