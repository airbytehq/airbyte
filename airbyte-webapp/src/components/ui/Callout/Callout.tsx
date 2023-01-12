import { IconDefinition } from "@fortawesome/fontawesome-svg-core";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";

import styles from "./Callout.module.scss";

interface Props {
  className?: string;
  icon?: IconDefinition;
  variant?: "default" | "error";
}

export const Callout: React.FC<React.PropsWithChildren<Props>> = ({
  children,
  className,
  icon,
  variant = "default",
}) => {
  const containerStyles = classNames(styles.container, className, {
    [styles.default]: variant === "default",
    [styles.error]: variant === "error",
  });

  return (
    <div className={containerStyles}>
      {icon && <FontAwesomeIcon size="lg" icon={icon} />}
      {children}
    </div>
  );
};
