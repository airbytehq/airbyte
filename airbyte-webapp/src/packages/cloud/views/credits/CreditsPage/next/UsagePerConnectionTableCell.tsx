import { PropsWithChildren } from "react";

import { FlexContainer } from "components/ui/Flex";

export const UsagePerConnectionTableCell: React.FC<PropsWithChildren<unknown>> = ({ children }) => {
  return <FlexContainer>{children}</FlexContainer>;
};
