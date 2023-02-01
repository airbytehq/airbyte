import classNames from "classnames";

import styles from "./Overlay.module.scss";

interface OverlayProps {
  onClick?: React.MouseEventHandler<HTMLDivElement>;
  variant?: "dark" | "transparent";
}

export const Overlay: React.FC<OverlayProps> = ({ variant = "dark", onClick }) => (
  <div
    className={classNames(styles.container, {
      [styles.dark]: variant === "dark",
    })}
    role={onClick ? "button" : undefined}
    onClick={onClick}
    aria-hidden="true"
    data-test-id="overlayContainer"
  />
);
