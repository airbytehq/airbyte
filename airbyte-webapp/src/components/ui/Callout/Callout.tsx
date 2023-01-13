import classNames from "classnames";

import styles from "./Callout.module.scss";

interface CalloutProps {
  className?: string;
  variant?: "default" | "error" | "info";
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
  });

  return <div className={containerStyles}>{children}</div>;
};
