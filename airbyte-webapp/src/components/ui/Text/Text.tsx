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
  inverseColor?: boolean;
  title?: string;
}

const getTextClassNames = ({
  size,
  centered,
  bold,
  inverseColor,
}: Required<Pick<TextProps, "size" | "centered" | "bold" | "inverseColor">>) => {
  const sizes: Record<TextSize, string> = {
    xs: styles.xs,
    sm: styles.sm,
    md: styles.md,
    lg: styles.lg,
  };

  return classNames(styles.text, sizes[size], {
    [styles.centered]: centered,
    [styles.bold]: bold,
    [styles.inverse]: inverseColor,
  });
};

export const Text: React.FC<React.PropsWithChildren<TextProps>> = React.memo(
  ({
    as = "p",
    bold = false,
    centered = false,
    children,
    className: classNameProp,
    size = "md",
    inverseColor = false,
    ...remainingProps
  }) => {
    const className = classNames(getTextClassNames({ centered, size, bold, inverseColor }), classNameProp);

    return React.createElement(as, {
      ...remainingProps,
      "data-type": "text",
      className,
      children,
    });
  }
);
