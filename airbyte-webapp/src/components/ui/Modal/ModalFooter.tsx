import styles from "./ModalFooter.module.scss";

export const ModalFooter: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => {
  return <div className={styles.modalFooter}>{children}</div>;
};
