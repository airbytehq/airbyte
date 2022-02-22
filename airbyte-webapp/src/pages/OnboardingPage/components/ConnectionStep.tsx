import React from "react";
import { FormattedMessage } from "react-intl";

import CreateConnectionContent from "components/CreateConnectionContent";
import { Destination, Source } from "core/domain/connector";
import TitlesBlock from "./TitlesBlock";
import HighlightedText from "./HighlightedText";

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
        source={source}
        destination={destination}
        afterSubmitConnection={afterSubmitConnection}
      />
    </>
  );
};

export default ConnectionStep;
