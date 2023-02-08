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
  color?: "default" | "grey-300";
}

const getTextClassNames = ({
  size,
  centered,
  bold,
  inverseColor,
  color,
}: Required<Pick<TextProps, "size" | "centered" | "bold" | "inverseColor" | "color">>) => {
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
    [styles["text--color-grey-300"]]: color === "grey-300",
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
    color = "default",
    ...remainingProps
  }) => {
    const className = classNames(getTextClassNames({ centered, size, bold, inverseColor, color }), classNameProp);

    return React.createElement(as, {
      ...remainingProps,
      "data-type": "text",
      className,
      children,
    });
  }
);
