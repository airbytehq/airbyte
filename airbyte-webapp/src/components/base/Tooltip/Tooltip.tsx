import { autoUpdate, flip, offset, shift, useFloating, UseFloatingProps } from "@floating-ui/react-dom";
import classNames from "classnames";
import { uniqueId } from "lodash";
import React, { useState, useEffect, useMemo } from "react";
import { createPortal } from "react-dom";

import { tooltipContext } from "./context";
import styles from "./Tooltip.module.scss";
import { TooltipProps } from "./types";

const MOUSE_OUT_TIMEOUT_MS = 50;

const FLOATING_OPTIONS: UseFloatingProps = {
  middleware: [
    offset(5), // $spacing-sm
    flip(),
    shift(),
  ],
  whileElementsMounted: autoUpdate,
};

export const Tooltip: React.FC<TooltipProps> = (props) => {
  const { children, control, className, disabled, cursor, theme = "dark", placement = "bottom" } = props;

  const [isOverTooltip, setIsOverTooltip] = useState(false);
  const [isVisible, setIsVisible] = useState(false);

  const tooltipId = useMemo(() => uniqueId("tooltip_"), []);

  const { x, y, reference, floating, strategy } = useFloating({
    ...FLOATING_OPTIONS,
    placement,
  });

  useEffect(() => {
    if (isOverTooltip) {
      setIsVisible(true);
      return;
    }

    const timeout = window.setTimeout(() => {
      setIsVisible(false);
    }, MOUSE_OUT_TIMEOUT_MS);

    return () => {
      window.clearTimeout(timeout);
    };
  }, [isOverTooltip]);

  const canShowTooltip = isVisible && !disabled;

  const onFocus = () => {
    setIsOverTooltip(true);
  };

  const onBlur = () => {
    setIsOverTooltip(false);
  };

  return (
    <>
      <div
        ref={reference}
        className={styles.container}
        style={disabled ? undefined : { cursor }}
        onFocus={onFocus}
        onBlur={onBlur}
        onMouseOver={onFocus}
        onMouseOut={onBlur}
        aria-details={tooltipId}
        tabIndex={0}
      >
        {control}
      </div>
      {canShowTooltip &&
        createPortal(
          <div
            role="tooltip"
            id={tooltipId}
            ref={floating}
            className={classNames(styles.tooltip, theme === "light" && styles.light, className)}
            style={{
              position: strategy,
              top: y ?? 0,
              left: x ?? 0,
            }}
            onFocus={onFocus}
            onBlur={onBlur}
            onMouseOver={onFocus}
            onMouseOut={onBlur}
          >
            <tooltipContext.Provider value={props}>{children}</tooltipContext.Provider>
          </div>,
          document.body
        )}
    </>
  );
};
