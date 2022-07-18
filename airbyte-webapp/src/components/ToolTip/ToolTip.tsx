import classNames from "classnames";
import React, { useState, useEffect } from "react";
import TetherComponent from "react-tether";

import styles from "./ToolTip.module.scss";

type ToolTipCursor = "pointer" | "help" | "not-allowed" | "initial";
type ToolTipMode = "dark" | "light";
type ToolTipAlignment = "top" | "right" | "bottom" | "left";

interface ToolTipProps {
  control: React.ReactNode;
  className?: string;
  disabled?: boolean;
  cursor?: ToolTipCursor;
  mode?: ToolTipMode;
  align?: ToolTipAlignment;
}

const MOUSE_OUT_TIMEOUT_MS: Readonly<number> = 50;

const TETHER_ATTACHMENT_BY_ALIGNMENT: Readonly<Record<ToolTipAlignment, string>> = {
  top: "bottom center",
  right: "middle left",
  bottom: "top center",
  left: "middle right",
};

export const ToolTip: React.FC<ToolTipProps> = ({
  children,
  control,
  className,
  disabled,
  cursor,
  mode = "dark",
  align = "bottom",
}) => {
  const [isMouseOver, setIsMouseOver] = useState(false);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (isMouseOver) {
      setIsVisible(true);
      return;
    }

    const timeout = window.setTimeout(() => {
      setIsVisible(false);
    }, MOUSE_OUT_TIMEOUT_MS);

    return () => {
      window.clearTimeout(timeout);
    };
  }, [isMouseOver]);

  const canShowTooltip = isVisible && !disabled;

  const onMouseOver = () => {
    setIsMouseOver(true);
  };

  const onMouseOut = () => {
    setIsMouseOver(false);
  };

  return (
    <TetherComponent
      attachment={TETHER_ATTACHMENT_BY_ALIGNMENT[align]}
      renderTarget={(ref) => (
        <div
          ref={ref as React.LegacyRef<HTMLDivElement>}
          className={styles.container}
          style={disabled ? undefined : { cursor }}
          onMouseOver={onMouseOver}
          onMouseOut={onMouseOut}
        >
          {control}
        </div>
      )}
      renderElement={(ref) =>
        canShowTooltip && (
          <div
            ref={ref as React.LegacyRef<HTMLDivElement>}
            className={classNames(styles.toolTip, mode === "light" && styles.light, className)}
            onMouseOver={onMouseOver}
            onMouseOut={onMouseOut}
          >
            {children}
          </div>
        )
      }
    />
  );
};
