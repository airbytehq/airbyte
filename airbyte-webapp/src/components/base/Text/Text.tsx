import classNames from "classnames";
import React, { useMemo } from "react";

import headingStyles from "./heading.module.scss";
import textStyles from "./text.module.scss";

type TextSize = "sm" | "md" | "lg" | "xl";
type TextElementType = "h1" | "h2" | "h3" | "h4" | "h5" | "h6" | "p" | "span" | "div";

interface TextProps {
  as?: TextElementType;
  size?: TextSize;
  className?: string;
  bold?: boolean;
  centered?: boolean;
}

const getTextClassNames = ({ size, centered, bold }: Required<Pick<TextProps, "size" | "centered" | "bold">>) => {
  const sizes: Partial<Record<TextSize, string>> = {
    sm: textStyles.sm,
    lg: textStyles.lg,
    xl: textStyles.xl,
  };

  return classNames(textStyles.text, sizes[size], centered && textStyles.centered, bold && textStyles.bold);
};

const getHeadingClassNames = ({ size, centered }: Required<Pick<TextProps, "size" | "centered">>) => {
  const sizes: Partial<Record<TextSize, string>> = {
    sm: headingStyles.sm,
    lg: headingStyles.lg,
    xl: headingStyles.xl,
  };

  return classNames(headingStyles.heading, sizes[size], centered && headingStyles.centered);
};

export const Text: React.FC<TextProps> = ({
  as = "p",
  size = "md",
  bold = false,
  centered = false,
  className: customClassName,
  children,
}) => {
  const className = useMemo(() => {
    const isHeading = /^h[0-6]$/.test(as);
    return classNames(
      isHeading ? getHeadingClassNames({ size, centered }) : getTextClassNames({ size, centered, bold }),
      customClassName
    );
  }, [as, bold, centered, customClassName, size]);

  return React.createElement(as, {
    className,
    children,
  });
};
