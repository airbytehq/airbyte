import styles from "./ModalBody.module.scss";

interface ModalBodyProps {
  maxHeight?: number | string;
}

export const ModalBody: React.FC<ModalBodyProps> = ({ children, maxHeight }) => {
  return (
    <div className={styles.modalBody} style={{ maxHeight }}>
      {children}
    </div>
  );
};
