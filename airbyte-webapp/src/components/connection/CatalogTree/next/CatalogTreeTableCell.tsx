import classNames from "classnames";
import React, { useCallback, useEffect, useRef, useState } from "react";
import { useWindowSize } from "react-use";

import { TextWithHTML } from "components/ui/TextWithHTML";
import { Tooltip } from "components/ui/Tooltip";

import styles from "./CatalogTreeTableCell.module.scss";

type Sizes = "xsmall" | "small" | "medium" | "large";

interface CatalogTreeTableCellProps {
  size?: Sizes;
  className?: string;
  withTooltip?: boolean;
}

// This lets us avoid the eslint complaint about unused styles
const sizeMap: Readonly<Record<Sizes, string>> = {
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
  return <TextWithHTML text={text} />;
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
    if (!withTooltip) {
      return;
    }

    // windowWidth is only here so this functionality changes based on window width
    if (windowWidth && textNodes.length) {
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

      setTooltipDisabled(scrollWidths <= clientWidths);
    }
  }, [textNodes, windowWidth, withTooltip]);

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
