import React from "react";

import CreateConnectionContent from "components/CreateConnectionContent";
import TitlesBlock from "./TitlesBlock";
import { FormattedMessage } from "react-intl";
import HighlightedText from "./HighlightedText";
import { Destination, Source } from "core/domain/connector";

type IProps = {
  errorStatus?: number;
  source: Source;
  destination: Destination;
  afterSubmitConnection: () => void;
};

const ConnectionStep: React.FC<IProps> = ({
  source,
  destination,
  afterSubmitConnection,
}) => {
  return (
    <>
      <TitlesBlock
        title={
          <FormattedMessage
            id="onboarding.createConnection"
            values={{
              name: (...name: React.ReactNode[]) => (
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
        source={source}
        destination={destination}
        afterSubmitConnection={afterSubmitConnection}
      />
    </>
  );
};

export default ConnectionStep;
