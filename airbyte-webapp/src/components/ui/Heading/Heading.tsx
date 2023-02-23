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
  inverseColor?: boolean;
}

const getHeadingClassNames = ({
  size,
  centered,
  inverseColor,
}: Required<Pick<HeadingProps, "size" | "centered" | "inverseColor">>) => {
  const sizes: Record<HeadingSize, string> = {
    sm: styles.sm,
    md: styles.md,
    lg: styles.lg,
    xl: styles.xl,
  };

  return classNames(styles.heading, sizes[size], { [styles.centered]: centered, [styles.inverse]: inverseColor });
};

export const Heading: React.FC<React.PropsWithChildren<HeadingProps>> = React.memo(
  ({
    as,
    centered = false,
    children,
    className: classNameProp,
    size = "md",
    inverseColor = false,
    ...remainingProps
  }) => {
    const className = classNames(getHeadingClassNames({ centered, size, inverseColor }), classNameProp);

    return React.createElement(as, {
      ...remainingProps,
      className,
      children,
    });
  }
);
