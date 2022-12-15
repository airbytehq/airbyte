import classNames from "classnames";
import React from "react";

import styles from "./heading.module.scss";

type HeadingSize = "sm" | "md" | "lg" | "xl";
type HeadingElementType = "h1" | "h2" | "h3" | "h4" | "h5" | "h6";

interface HeadingProps {
  className?: string;
  centered?: boolean;
  as: HeadingElementType;
  size?: HeadingSize;
}

const getHeadingClassNames = ({ size, centered }: Required<Pick<HeadingProps, "size" | "centered">>) => {
  const sizes: Record<HeadingSize, string> = {
    sm: styles.sm,
    md: styles.md,
    lg: styles.lg,
    xl: styles.xl,
  };

  return classNames(styles.heading, sizes[size], centered && styles.centered);
};

export const Heading: React.FC<React.PropsWithChildren<HeadingProps>> = React.memo(
  ({ as, centered = false, children, className: classNameProp, size = "md", ...remainingProps }) => {
    const className = classNames(getHeadingClassNames({ centered, size }), classNameProp);

    return React.createElement(as, {
      ...remainingProps,
      className,
      children,
    });
  }
);
