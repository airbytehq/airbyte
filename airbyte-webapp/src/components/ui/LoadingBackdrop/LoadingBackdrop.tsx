import React from "react";

import { Spinner } from "components/ui/Spinner";

import styles from "./LoadingBackdrop.module.scss";

interface LoadingBackdropProps {
  loading: boolean;
  small?: boolean;
}
export const LoadingBackdrop: React.FC<React.PropsWithChildren<LoadingBackdropProps>> = ({
  loading,
  small,
  children,
}) => {
  return (
    <div className={styles.loadingBackdropContainer}>
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
