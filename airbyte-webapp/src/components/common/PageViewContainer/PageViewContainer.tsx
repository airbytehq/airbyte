import React from "react";

import { BaseClearView } from "./BaseClearView";
import { PaddedCard } from "./PaddedCard";

export const PageViewContainer: React.FC<React.PropsWithChildren<unknown>> = (props) => {
  return (
    <BaseClearView>
      <PaddedCard>{props.children}</PaddedCard>
    </BaseClearView>
  );
};
