import classNames from "classnames";

import styles from "./Callout.module.scss";

interface CalloutProps {
  className?: string;
  variant?: "yellow" | "red" | "blue";
}

export const Callout: React.FC<React.PropsWithChildren<CalloutProps>> = ({
  children,
  className,

  variant = "yellow",
}) => {
  const containerStyles = classNames(styles.container, className, {
    [styles.yellow]: variant === "yellow",
    [styles.red]: variant === "red",
    [styles.blue]: variant === "blue",
  });

  return <div className={containerStyles}>{children}</div>;
};
