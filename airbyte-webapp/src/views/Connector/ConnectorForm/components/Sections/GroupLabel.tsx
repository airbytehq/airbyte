import { FormConditionItem, FormObjectArrayItem } from "core/form/types";

import { PropertyLabel } from "../Property/PropertyLabel";

interface GroupLabelProps {
  formField: FormConditionItem | FormObjectArrayItem;
}

export const GroupLabel: React.FC<GroupLabelProps> = ({ formField }) => {
  return <PropertyLabel property={formField} label={`${formField.title || formField.fieldKey}`} optional={false} />;
};
