import styles from "./ModalBody.module.scss";

interface ModalBodyProps {
  width: number | string;
  maxHeight?: number | string;
}

export const ModalBody: React.FC<ModalBodyProps> = ({ children, maxHeight, width }) => {
  return (
    <div className={styles.modalBody} style={{ maxHeight, width }}>
      {children}
    </div>
  );
};
