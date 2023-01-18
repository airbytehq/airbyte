import classNames from "classnames";

import styles from "./Callout.module.scss";

interface CalloutProps {
  className?: string;
  variant?: "default" | "error" | "info" | "boldInfo";
}

export const Callout: React.FC<React.PropsWithChildren<CalloutProps>> = ({
  children,
  className,
  variant = "default",
}) => {
  const containerStyles = classNames(styles.container, className, {
    [styles.default]: variant === "default",
    [styles.error]: variant === "error",
    [styles.info]: variant === "info",
    [styles.boldInfo]: variant === "boldInfo",
  });

  return <div className={containerStyles}>{children}</div>;
};
