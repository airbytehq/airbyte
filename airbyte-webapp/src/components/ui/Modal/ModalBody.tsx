import classnames from "classnames";

import styles from "./ModalBody.module.scss";

interface ModalBodyProps {
  maxHeight?: number | string;
  padded?: boolean;
  className?: string;
}

export const ModalBody: React.FC<React.PropsWithChildren<ModalBodyProps>> = ({
  children,
  maxHeight,
  padded = true,
  className,
}) => {
  const modalStyles = classnames(
    styles.modalBody,
    {
      [styles.paddingNone]: !padded,
    },
    className
  );
  return (
    <div className={modalStyles} style={{ maxHeight }}>
      {children}
    </div>
  );
};
