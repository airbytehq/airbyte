import React from "react";

import BaseClearView from "components/BaseClearView";

import PaddedCard from "./PaddedCard";

const PageViewContainer: React.FC = (props) => {
  return (
    <BaseClearView>
      <PaddedCard>{props.children}</PaddedCard>
    </BaseClearView>
  );
};

export default PageViewContainer;
