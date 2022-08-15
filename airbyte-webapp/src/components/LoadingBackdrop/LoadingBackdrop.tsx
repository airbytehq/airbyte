import React from "react";

import Spinner from "../Spinner/Spinner";
import styles from "./LoadingBackdrop.module.scss";

interface LoadingBackdropProps {
  isActive: boolean;
  small?: boolean;
}
export const LoadingBackdrop: React.FC<LoadingBackdropProps> = ({ isActive, small, children }) => {
  return (
    <div className={styles.loadingBackdropContainer}>
      {isActive && (
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
