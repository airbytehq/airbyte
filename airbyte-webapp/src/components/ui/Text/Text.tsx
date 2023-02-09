import classNames from "classnames";
import React from "react";

import styles from "./Text.module.scss";

type TextSize = "xs" | "sm" | "md" | "lg";
type TextElementType = "p" | "span" | "div";

interface TextProps {
  className?: string;
  centered?: boolean;
  as?: TextElementType;
  size?: TextSize;
  bold?: boolean;
  title?: string;
  inverseColor?: boolean;
}

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
    const className = classNames(
      styles.text,
      {
        [styles["text--xs"]]: size === "xs",
        [styles["text--sm"]]: size === "sm",
        [styles["text--md"]]: size === "md",
        [styles["text--lg"]]: size === "lg",
        [styles["text--centered"]]: centered,
        [styles["text--bold"]]: bold,
        [styles["text--inverse"]]: inverseColor,
      },
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
