import classNames from "classnames";
import React from "react";

import headingStyles from "./heading.module.scss";
import textStyles from "./text.module.scss";

type TextSize = "sm" | "md" | "lg" | "xl";
type HeadingSize = TextSize | "xl";
type TextElementType = "p" | "span" | "div";
type HeadingElementType = "h1" | "h2" | "h3" | "h4" | "h5" | "h6";

interface BaseProps {
  className?: string;
  centered?: boolean;
}

interface TextProps extends BaseProps {
  as?: HeadingElementType;
  size?: TextSize;
  bold?: boolean;
}

interface HeadingProps extends BaseProps {
  as?: TextElementType;
  size?: HeadingSize;
}

const getTextClassNames = ({ size, centered, bold }: Required<Pick<TextProps, "size" | "centered" | "bold">>) => {
  const sizes: Partial<Record<TextSize, string>> = {
    sm: textStyles.sm,
    lg: textStyles.lg,
  };

  return classNames(textStyles.text, sizes[size], centered && textStyles.centered, bold && textStyles.bold);
};

const getHeadingClassNames = ({ size, centered }: Required<Pick<HeadingProps, "size" | "centered">>) => {
  const sizes: Partial<Record<TextSize, string>> = {
    sm: headingStyles.sm,
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
  const { as = isHeading ? "h1" : "p", size = "md", centered = false, children } = props;

  const className = classNames(
    isHeading
      ? getHeadingClassNames({ size, centered })
      : getTextClassNames({ size, centered, bold: props.bold ?? false }),
    props.className
  );

  return React.createElement(as, {
    className,
    children,
  });
});
