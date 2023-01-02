import classNames from "classnames";
import React, { HTMLAttributes } from "react";

import styles from "./FlexItem.module.scss";

interface FlexItemProps {
  className?: string;
  /**
   * Sets `flex-grow` to 1 if truthy
   */
  grow?: boolean;
  /**
   * The `self-align` css property
   */
  selfAlign?: "flex-start" | "flex-end" | "center" | "baseline" | "stretch";
}

/**
 * Renders a div element which sets css properties for flex children as given by the props.
 * This component can be used within a `FlexContainer` parent if grow or self-align props should be set, but it can also be omitted
 * in case no special flex properties are required.
 */
export const FlexItem: React.FC<React.PropsWithChildren<FlexItemProps & HTMLAttributes<HTMLDivElement>>> = ({
  className,
  grow,
  selfAlign,
  children,
  ...otherProps
}) => {
  const fullClassName = classNames(
    {
      [styles.grow]: grow,
      [styles.alignSelfStart]: selfAlign === "flex-start",
      [styles.alignSelfEnd]: selfAlign === "flex-end",
      [styles.alignSelfCenter]: selfAlign === "center",
      [styles.alignSelfBaseline]: selfAlign === "baseline",
      [styles.alignSelfStretch]: selfAlign === "stretch",
    },
    className
  );

  return (
    <div className={fullClassName} {...otherProps}>
      {children}
    </div>
  );
};
