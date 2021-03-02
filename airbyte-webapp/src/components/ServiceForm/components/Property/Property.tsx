import React from "react";

import { Control } from "./Control";
import { Label } from "./Label";
import { FormBaseItem } from "core/form/types";

type IProps = {
  property: FormBaseItem;
};

const Property: React.FC<IProps> = ({ property }) => {
  return (
    <Label property={property}>
      <Control property={property} />
    </Label>
  );
};

export { Property };
