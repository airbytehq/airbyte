import { faXmark } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

import styles from "./RemoveButton.module.scss";

export const RemoveButton = ({ onClick }: { onClick: () => void }) => {
  return (
    <button className={styles.removeButton} onClick={onClick}>
      <FontAwesomeIcon icon={faXmark} />
    </button>
  );
};
