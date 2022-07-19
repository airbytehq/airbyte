import classnames from "classnames";

import styles from "./ModalBody.module.scss";

interface ModalBodyProps {
  maxHeight?: number | string;
  padding?: boolean;
}

export const ModalBody: React.FC<ModalBodyProps> = ({ children, maxHeight, padding }) => {
  const modalStyles = classnames(styles.modalBody, {
    [styles.paddingNone]: padding === false,
  });
  return (
    <div className={modalStyles} style={{ maxHeight }}>
      {children}
    </div>
  );
};
