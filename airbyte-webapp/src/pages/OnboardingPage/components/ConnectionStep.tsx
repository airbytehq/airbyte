import React from "react";

import CreateConnectionContent from "components/CreateConnectionContent";
import { Source } from "core/resources/Source";
import { Destination } from "core/resources/Destination";
import { Routes } from "../../routes";
import useRouter from "components/hooks/useRouterHook";
import SkipOnboardingButton from "./SkipOnboardingButton";
import TitlesBlock from "./TitlesBlock";
import { FormattedMessage } from "react-intl";
import HighlightedText from "./HighlightedText";

type IProps = {
  errorStatus?: number;
  source: Source;
  destination: Destination;
};

const ConnectionStep: React.FC<IProps> = ({ source, destination }) => {
  const { push } = useRouter();

  const afterSubmitConnection = () => push(Routes.Root);

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
        additionBottomControls={<SkipOnboardingButton step="connection" />}
        source={source}
        destination={destination}
        afterSubmitConnection={afterSubmitConnection}
      />
    </>
  );
};

export default ConnectionStep;
