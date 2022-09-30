import React from "react";

import { CreateConnection } from "components/CreateConnection/CreateConnection";

import { useDestinationList } from "hooks/services/useDestinationHook";
import { useSourceList } from "hooks/services/useSourceHook";

interface ConnectionStepProps {
  onNextStep: () => void;
}

const ConnectionStep: React.FC<ConnectionStepProps> = ({ onNextStep: afterSubmitConnection }) => {
  const { sources } = useSourceList();
  const { destinations } = useDestinationList();

  return (
    <CreateConnection source={sources[0]} destination={destinations[0]} afterSubmitConnection={afterSubmitConnection} />
  );
};

export default ConnectionStep;
