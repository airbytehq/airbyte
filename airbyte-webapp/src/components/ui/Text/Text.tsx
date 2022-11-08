import classNames from "classnames";
import React from "react";

import styles from "./text.module.scss";

type TextSize = "xs" | "sm" | "md" | "lg";
type TextElementType = "p" | "span" | "div";

interface TextProps {
  className?: string;
  centered?: boolean;
  as?: TextElementType;
  size?: TextSize;
  bold?: boolean;
}

const getTextClassNames = ({ size, centered, bold }: Required<Pick<TextProps, "size" | "centered" | "bold">>) => {
  const sizes: Record<TextSize, string> = {
    xs: styles.xs,
    sm: styles.sm,
    md: styles.md,
    lg: styles.lg,
  };

  return classNames(styles.text, sizes[size], centered && styles.centered, bold && styles.bold);
};

export const Text: React.FC<React.PropsWithChildren<TextProps>> = React.memo(
  ({
    as = "p",
    bold = false,
    centered = false,
    children,
    className: classNameProp,
    size = "md",
    ...remainingProps
  }) => {
    const className = classNames(getTextClassNames({ centered, size, bold }), classNameProp);

    return React.createElement(as, {
      ...remainingProps,
      className,
      children,
    });
  }
);
