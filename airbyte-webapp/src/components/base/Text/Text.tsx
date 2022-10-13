import classNames from "classnames";
import React from "react";

import headingStyles from "./heading.module.scss";
import textStyles from "./text.module.scss";

type TextSize = "sm" | "md" | "lg";
type HeadingSize = TextSize | "xl";
type TextElementType = "p" | "span" | "div";
type HeadingElementType = "h1" | "h2" | "h3" | "h4" | "h5" | "h6";

interface BaseProps {
  className?: string;
  centered?: boolean;
}

interface TextProps extends BaseProps {
  as?: TextElementType;
  size?: TextSize;
  bold?: boolean;
}

interface HeadingProps extends BaseProps {
  as: HeadingElementType;
  size?: HeadingSize;
}

const getTextClassNames = ({ size, centered, bold }: Required<Pick<TextProps, "size" | "centered" | "bold">>) => {
  const sizes: Record<TextSize, string> = {
    sm: textStyles.sm,
    md: textStyles.md,
    lg: textStyles.lg,
  };

  return classNames(textStyles.text, sizes[size], centered && textStyles.centered, bold && textStyles.bold);
};

const getHeadingClassNames = ({ size, centered }: Required<Pick<HeadingProps, "size" | "centered">>) => {
  const sizes: Record<HeadingSize, string> = {
    sm: headingStyles.sm,
    md: headingStyles.md,
    lg: headingStyles.lg,
    xl: headingStyles.xl,
  };

  return classNames(headingStyles.heading, sizes[size], centered && headingStyles.centered);
};

const isHeadingType = (props: TextProps | HeadingProps): props is HeadingProps => {
  return props.as ? /^h[0-6]$/.test(props.as) : false;
};

export const Text: React.FC<TextProps | HeadingProps> = React.memo((props) => {
  const isHeading = isHeadingType(props);
  const { as = "p", centered = false, children } = props;

  const className = classNames(
    isHeading
      ? getHeadingClassNames({ centered, size: props.size ?? "md" })
      : getTextClassNames({ centered, size: props.size ?? "md", bold: props.bold ?? false }),
    props.className
  );

  return React.createElement(as, {
    className,
    children,
  });
});
