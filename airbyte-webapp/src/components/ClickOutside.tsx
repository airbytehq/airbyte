import React, { createElement, useCallback, useEffect, useRef } from "react";

interface Props {
  type?: "span" | "div" | "a" | "p" | "text" | "nav";
  className?: string;
  onClickIn?: () => void | null;
  onClickOut?: () => void | null;
}

const ClickOutside: React.FC<Props> = ({
  children,
  type = "div",
  className = "",

  onClickIn = () => null,
  onClickOut = () => null,

  ...props
}) => {
  const context = useRef<HTMLElement>(null);

  const handleElementClick = useCallback(onClickIn, [onClickIn]);

  const handleDocumentClick = useCallback(
    (event) => {
      const isTouch = event.type === "touchend";

      if (event.type === "click" && isTouch) {
        return false;
      }

      if (!context?.current?.contains(event.target)) {
        onClickOut();
      }

      return true;
    },
    [onClickOut]
  );

  useEffect(() => {
    document.addEventListener("touchend", handleDocumentClick, true);
    document.addEventListener("click", handleDocumentClick, true);

    return () => {
      document.removeEventListener("touchend", handleDocumentClick, true);
      document.removeEventListener("click", handleDocumentClick, true);
    };
  });

  return createElement(
    type,
    { ref: context, onClick: handleElementClick, className, ...props },
    children
  );
};

export default ClickOutside;
