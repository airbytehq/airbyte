import { flip, offset, shift, useFloating } from "@floating-ui/react-dom";
import classNames from "classnames";
import React, { useState, useEffect } from "react";

import { tooltipContext } from "./context";
import styles from "./ToolTip.module.scss";
import { ToolTipProps } from "./types";

const MOUSE_OUT_TIMEOUT_MS = 50;

export const ToolTip: React.FC<ToolTipProps> = (props) => {
  const { children, control, className, disabled, cursor, theme = "dark", placement = "bottom" } = props;

  const [isMouseOver, setIsMouseOver] = useState(false);
  const [isVisible, setIsVisible] = useState(false);

  const { x, y, reference, floating, strategy } = useFloating({
    placement,
    middleware: [
      offset(5), // $spacing-sm
      flip(),
      shift(),
    ],
  });

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
    <>
      <div
        ref={reference}
        className={styles.container}
        style={disabled ? undefined : { cursor }}
        onMouseOver={onMouseOver}
        onMouseOut={onMouseOut}
      >
        {control}
      </div>
      {canShowTooltip && (
        <div
          role="tooltip"
          ref={floating}
          className={classNames(styles.tooltip, theme === "light" && styles.light, className)}
          style={{
            position: strategy,
            top: y ?? 0,
            left: x ?? 0,
          }}
          onMouseOver={onMouseOver}
          onMouseOut={onMouseOut}
        >
          <tooltipContext.Provider value={props}>{children}</tooltipContext.Provider>
        </div>
      )}
    </>
  );
};
