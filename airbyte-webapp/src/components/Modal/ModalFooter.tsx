import styles from "./ModalFooter.module.scss";

export const ModalFooter: React.FC = ({ children }) => {
  return <div className={styles.modalFooter}>{children}</div>;
};
