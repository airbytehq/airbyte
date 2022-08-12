import classNames from "classnames";
import React, { useMemo } from "react";

import styles from "./Text.module.scss";

type TextSize = "sm" | "md" | "lg" | "xl";
type TextElementType = "h1" | "h2" | "h3" | "h4" | "h5" | "h6" | "p" | "span" | "div";

interface TextProps {
  as?: TextElementType;
  size?: TextSize;
  className?: string;
  bold?: boolean;
  centered?: boolean;
}

const getSizeClassName = (size: TextSize): string | undefined => {
  switch (size) {
    case "sm":
      return styles.sm;
    case "lg":
      return styles.lg;
    case "xl":
      return styles.xl;
  }

  return undefined;
};

export const Text: React.FC<TextProps> = ({
  as = "span",
  size = "md",
  bold,
  centered,
  className: customClassName,
  children,
}) => {
  const className = useMemo(() => {
    const isHeading = as.match(/^h[0-6]$/);
    return classNames(
      isHeading ? styles.heading : styles.text,
      getSizeClassName(size),
      { [styles.bold]: bold, [styles.centered]: centered },
      customClassName
    );
  }, [as, bold, centered, customClassName, size]);

  return React.createElement(as, {
    className,
    children,
  });
};
