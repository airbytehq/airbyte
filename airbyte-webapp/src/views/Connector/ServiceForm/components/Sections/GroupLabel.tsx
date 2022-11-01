import { FormConditionItem, FormObjectArrayItem } from "core/form/types";

import { PropertyLabel } from "../Property/PropertyLabel";
import styles from "./GroupLabel.module.scss";

interface GroupLabelProps {
  formField: FormConditionItem | FormObjectArrayItem;
}

export const GroupLabel: React.FC<GroupLabelProps> = ({ formField }) => {
  return (
    <PropertyLabel
      className={styles.groupLabel}
      property={formField}
      label={`${formField.title || formField.fieldKey}`}
      optional={false}
    />
  );
};
