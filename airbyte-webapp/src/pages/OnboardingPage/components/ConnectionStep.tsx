import React from "react";

import { CreateConnectionForm } from "components/CreateConnection/CreateConnectionForm";

import { useDestinationList } from "hooks/services/useDestinationHook";
import { useSourceList } from "hooks/services/useSourceHook";

interface ConnectionStepProps {
  onNextStep: () => void;
}

const ConnectionStep: React.FC<ConnectionStepProps> = ({ onNextStep: afterSubmitConnection }) => {
  const { sources } = useSourceList();
  const { destinations } = useDestinationList();

  return (
    <CreateConnectionForm
      source={sources[0]}
      destination={destinations[0]}
      afterSubmitConnection={afterSubmitConnection}
    />
  );
};

export default ConnectionStep;
