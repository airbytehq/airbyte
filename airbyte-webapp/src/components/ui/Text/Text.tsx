import classNames from "classnames";
import React from "react";

import styles from "./text.module.scss";

type TextSize = "xs" | "sm" | "md" | "lg";
type TextColor = "darkBlue" | "grey";
type TextElementType = "p" | "span" | "div";

interface TextProps {
  className?: string;
  centered?: boolean;
  as?: TextElementType;
  size?: TextSize;
  color?: TextColor;
  bold?: boolean;
  inverseColor?: boolean;
  title?: string;
  gradient?: boolean;
}

const getTextClassNames = ({
  size,
  color,
  centered,
  bold,
  inverseColor,
  gradient,
}: Required<Pick<TextProps, "size" | "color" | "centered" | "bold" | "inverseColor" | "gradient">>) => {
  const sizes: Record<TextSize, string> = {
    xs: styles.xs,
    sm: styles.sm,
    md: styles.md,
    lg: styles.lg,
  };

  const colors: Record<TextColor, string> = {
    darkBlue: styles.darkBlue,
    grey: styles.grey,
  };

  return classNames(styles.text, sizes[size], colors[color], {
    [styles.centered]: centered,
    [styles.bold]: bold,
    [styles.inverse]: inverseColor,
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
    color = "darkBlue",
    inverseColor = false,
    gradient = false,
    ...remainingProps
  }) => {
    const className = classNames(
      getTextClassNames({ centered, size, color, bold, inverseColor, gradient }),
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
