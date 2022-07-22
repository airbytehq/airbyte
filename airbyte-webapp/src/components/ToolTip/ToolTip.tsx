import classNames from "classnames";
import React, { useState, useEffect } from "react";
import TetherComponent from "react-tether";

import { tooltipContext } from "./context";
import styles from "./ToolTip.module.scss";
import { ToolTipAlignment, ToolTipProps } from "./types";

const MOUSE_OUT_TIMEOUT_MS: Readonly<number> = 50;

const TETHER_ATTACHMENT_BY_ALIGNMENT: Readonly<Record<ToolTipAlignment, string>> = {
  top: "bottom center",
  right: "middle left",
  bottom: "top center",
  left: "middle right",
};

export const ToolTip: React.FC<ToolTipProps> = (props) => {
  const { children, control, className, disabled, cursor, theme = "dark", align = "bottom" } = props;

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
            className={classNames(styles.toolTip, theme === "light" && styles.light, className)}
            onMouseOver={onMouseOver}
            onMouseOut={onMouseOut}
          >
            <tooltipContext.Provider value={props}>{children}</tooltipContext.Provider>
          </div>
        )
      }
    />
  );
};
