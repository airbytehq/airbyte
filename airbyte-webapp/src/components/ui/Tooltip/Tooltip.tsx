/* eslint-disable jsx-a11y/mouse-events-have-key-events */
import { autoUpdate, flip, offset, shift, useFloating, UseFloatingProps } from "@floating-ui/react-dom";
import classNames from "classnames";
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

export const Tooltip: React.FC<React.PropsWithChildren<TooltipProps>> = (props) => {
  const {
    children,
    control,
    className,
    containerClassName,
    disabled,
    cursor,
    theme = "dark",
    placement = "bottom",
  } = props;

  const [isMouseOver, setIsMouseOver] = useState(false);
  const [isVisible, setIsVisible] = useState(false);

  const { x, y, reference, floating, strategy } = useFloating({
    ...FLOATING_OPTIONS,
    placement,
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

  const canShowTooltip = useMemo(() => isVisible && !disabled, [disabled, isVisible]);

  const onMouseOver = () => {
    setIsMouseOver(true);
  };

  const onMouseOut = () => {
    setIsMouseOver(false);
  };

  return (
    <>
      <span
        ref={reference}
        className={classNames(styles.container, containerClassName)}
        style={disabled ? undefined : { cursor }}
        onMouseOver={onMouseOver}
        onMouseOut={onMouseOut}
      >
        {control}
      </span>
      {createPortal(
        canShowTooltip ? (
          <div
            role="tooltip"
            ref={floating}
            className={classNames(
              styles.tooltip,
              {
                [styles.light]: theme === "light",
              },
              className
            )}
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
        ) : null,
        document.body
      )}
    </>
  );
};
