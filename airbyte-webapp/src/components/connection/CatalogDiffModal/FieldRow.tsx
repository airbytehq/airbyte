import { faMinus, faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classnames from "classnames";

import { ArrowRightIcon } from "components/icons/ArrowRightIcon";
import { ModificationIcon } from "components/icons/ModificationIcon";

import { FieldTransform } from "core/request/AirbyteClient";

import styles from "./FieldRow.module.scss";

interface FieldRowProps {
  transform: FieldTransform;
}

export const FieldRow: React.FC<FieldRowProps> = ({ transform }) => {
  const fieldName = transform.fieldName.join(".");
  const diffType = transform.transformType.includes("add")
    ? "add"
    : transform.transformType.includes("remove")
    ? "remove"
    : "update";

  const oldType = transform.updateFieldSchema?.oldSchema.type;
  const newType = transform.updateFieldSchema?.newSchema.type;

  const iconStyle = classnames(styles.icon, {
    [styles.plus]: diffType === "add",
    [styles.minus]: diffType === "remove",
    [styles.mod]: diffType === "update",
  });

  const contentStyle = classnames(styles.content, styles.cell, {
    [styles.add]: diffType === "add",
    [styles.remove]: diffType === "remove",
    [styles.update]: diffType === "update",
  });

  const updateCellStyle = classnames(styles.cell, styles.update);
  const hasTypeChange = oldType && newType;

  return (
    <tr
      className={classnames(styles.row, {
        [styles.withType]: hasTypeChange,
      })}
    >
      <td className={contentStyle}>
        <div className={styles.iconContainer}>
          {diffType === "add" ? (
            <FontAwesomeIcon icon={faPlus} size="1x" className={iconStyle} />
          ) : diffType === "remove" ? (
            <FontAwesomeIcon icon={faMinus} size="1x" className={iconStyle} />
          ) : (
            <div className={iconStyle}>
              <ModificationIcon />
            </div>
          )}
        </div>
        <div title={fieldName} className={styles.fieldName}>
          {fieldName}
        </div>
      </td>
      {hasTypeChange && (
        <td className={contentStyle}>
          <div className={updateCellStyle}>
            <span className={styles.dataType}>
              {oldType} <ArrowRightIcon /> {newType}
            </span>
          </div>
        </td>
      )}
    </tr>
  );
};
