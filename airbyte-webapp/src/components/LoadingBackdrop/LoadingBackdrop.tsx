import classNames from "classnames";
import React from "react";

import Spinner from "../Spinner/Spinner";
import styles from "./LoadingBackdrop.module.scss";

interface LoadingBackdropProps {
  loading: boolean;
  small?: boolean;
  className?: string;
}
export const LoadingBackdrop: React.FC<React.PropsWithChildren<LoadingBackdropProps>> = ({
  loading,
  small,
  children,
  className,
}) => {
  return (
    <div className={classNames(styles.loadingBackdropContainer, className)}>
      {loading && (
        <>
          <div className={styles.backdrop} data-testid="loading-backdrop" />
          <div className={styles.spinnerContainer}>
            <Spinner small={small} />
          </div>
        </>
      )}
      {children}
    </div>
  );
};
