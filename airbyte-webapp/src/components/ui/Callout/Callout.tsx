import { IconDefinition } from "@fortawesome/fontawesome-svg-core";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";

import styles from "./Callout.module.scss";

interface Props {
  className?: string;
  icon?: IconDefinition;
  variant?: "yellow" | "red";
  compact?: boolean;
}

export const Callout: React.FC<React.PropsWithChildren<Props>> = ({
  children,
  className,
  icon,
  variant = "yellow",
  compact = false,
}) => {
  const containerStyles = classNames(styles.container, className, {
    [styles.yellow]: variant === "yellow",
    [styles.red]: variant === "red",
    [styles.compact]: compact,
  });

  return (
    <div className={containerStyles}>
      {icon && <FontAwesomeIcon size="lg" icon={icon} />}
      {children}
    </div>
  );
};
