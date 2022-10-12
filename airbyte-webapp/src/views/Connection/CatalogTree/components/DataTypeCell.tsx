import React from "react";

import { Cell } from "components/SimpleTableComponents";

const DataTypeCell: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => {
  return <Cell>{children}</Cell>;
};

export default DataTypeCell;
