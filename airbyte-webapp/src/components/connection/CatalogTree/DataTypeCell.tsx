import React from "react";

import { Cell } from "components/SimpleTableComponents";

const DataTypeCell: React.FC<React.PropsWithChildren<unknown>> = ({ children, ...restProps }) => {
  return <Cell {...restProps}>{children}</Cell>;
};

export default DataTypeCell;
