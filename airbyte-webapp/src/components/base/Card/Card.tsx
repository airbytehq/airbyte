import classNames from "classnames";

import styles from "./Card.module.scss";

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  full?: boolean;
}

export const Card: React.FC<CardProps> = ({ children, full, ...props }) => (
  <div
    {...props}
    className={classNames(
      styles.card,
      {
        [styles.full]: full,
      },
      props.className
    )}
  >
    {children}
  </div>
);
