import { faMinus, faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classnames from "classnames";

import { FieldTransform } from "core/request/AirbyteClient";

import styles from "./FieldRow.module.scss";
import { ModificationIcon } from "./ModificationIcon";

interface FieldRowProps {
  transform: FieldTransform;
}

export const FieldRow: React.FC<FieldRowProps> = ({ transform }) => {
  // const transformType = transform.transformType;
  const fieldName = transform.fieldName[transform.fieldName.length - 1];
  const diffType = transform.transformType.includes("add")
    ? "add"
    : transform.transformType.includes("remove")
    ? "remove"
    : "update";
  const fieldType = transform.updateFieldSchema?.newSchema.type;

  const contentStyle = classnames(styles.rowContent, {
    [styles.add]: diffType === "add",
    [styles.remove]: diffType === "remove",
  });

  const iconStyle = classnames(styles.icon, {
    [styles.plus]: diffType === "add",
    [styles.minus]: diffType === "remove",
    [styles.mod]: diffType === "update",
  });

  return (
    <tr className={styles.row}>
      <td>
        {diffType === "add" ? (
          <FontAwesomeIcon icon={faPlus} size="1x" className={iconStyle} />
        ) : diffType === "remove" ? (
          <FontAwesomeIcon icon={faMinus} size="1x" className={iconStyle} />
        ) : (
          <ModificationIcon />
        )}
      </td>
      <td className={contentStyle}>{fieldName}</td>
      <td className={contentStyle}>{fieldType}</td>
    </tr>
  );
};
