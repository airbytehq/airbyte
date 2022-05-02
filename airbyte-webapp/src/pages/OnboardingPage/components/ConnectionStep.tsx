import React from "react";
import { FormattedMessage } from "react-intl";

import CreateConnectionContent from "components/CreateConnectionContent";

import { useDestinationList } from "hooks/services/useDestinationHook";
import { useSourceList } from "hooks/services/useSourceHook";

import HighlightedText from "./HighlightedText";
import TitlesBlock from "./TitlesBlock";

type IProps = {
  onNextStep: () => void;
};

const ConnectionStep: React.FC<IProps> = ({ onNextStep: afterSubmitConnection }) => {
  const { sources } = useSourceList();
  const { destinations } = useDestinationList();

  return (
    <>
      <TitlesBlock
        title={
          <FormattedMessage
            id="onboarding.createConnection"
            values={{
              name: (name: React.ReactNode[]) => <HighlightedText>{name}</HighlightedText>,
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
