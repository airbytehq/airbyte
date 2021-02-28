import React from "react";

import PaddedCard from "./PaddedCard";
import BaseClearView from "components/BaseClearView";

const PageViewContainer: React.FC = (props) => {
  return (
    <BaseClearView>
      <PaddedCard>{props.children}</PaddedCard>
    </BaseClearView>
  );
};

export default PageViewContainer;
