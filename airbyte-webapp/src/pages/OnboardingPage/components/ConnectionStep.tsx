import React from "react";
import { FormattedMessage } from "react-intl";

import CreateConnectionContent from "components/CreateConnectionContent";
import TitlesBlock from "./TitlesBlock";
import HighlightedText from "./HighlightedText";
import { useSourceList } from "hooks/services/useSourceHook";
import { useDestinationList } from "hooks/services/useDestinationHook";

type IProps = {
  onNextStep: () => void;
};

const ConnectionStep: React.FC<IProps> = ({
  onNextStep: afterSubmitConnection,
}) => {
  const { sources } = useSourceList();
  const { destinations } = useDestinationList();

  return (
    <>
      <TitlesBlock
        title={
          <FormattedMessage
            id="onboarding.createConnection"
            values={{
              name: (name: React.ReactNode[]) => (
                <HighlightedText>{name}</HighlightedText>
              ),
            }}
          />
        }
      >
        <FormattedMessage id="onboarding.createConnection.text" />
      </TitlesBlock>
      <CreateConnectionContent
        noTitles
        source={sources[0]}
        destination={destinations[0]}
        afterSubmitConnection={afterSubmitConnection}
      />
    </>
  );
};

export default ConnectionStep;
