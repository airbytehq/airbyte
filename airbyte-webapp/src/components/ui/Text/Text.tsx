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
  gradient?: boolean;
}

const getTextClassNames = ({
  size,
  centered,
  bold,
  inverseColor,
  color,
  gradient,
}: Required<Pick<TextProps, "size" | "centered" | "bold" | "inverseColor" | "color" | "gradient">>) => {
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
    [styles.gradient]: gradient,
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
    gradient = false,
    ...remainingProps
  }) => {
    const className = classNames(
      getTextClassNames({ centered, size, bold, inverseColor, gradient, color }),
      classNameProp
    );

    return React.createElement(as, {
      ...remainingProps,
      "data-type": "text",
      className,
      children,
    });
  }
);
