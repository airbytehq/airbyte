import React from "react";

import CreateConnectionContent from "components/CreateConnectionContent";

import { useDestinationList } from "hooks/services/useDestinationHook";
import { useSourceList } from "hooks/services/useSourceHook";

interface IProps {
  onNextStep: () => void;
}

const ConnectionStep: React.FC<IProps> = ({ onNextStep: afterSubmitConnection }) => {
  const { sources } = useSourceList();
  const { destinations } = useDestinationList();

  return (
    <CreateConnectionContent
      source={sources[0]}
      destination={destinations[0]}
      afterSubmitConnection={afterSubmitConnection}
    />
  );
};

export default ConnectionStep;
