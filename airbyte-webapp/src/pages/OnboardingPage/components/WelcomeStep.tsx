import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import TitlesBlock from "./TitlesBlock";
import HighlightedText from "./HighlightedText";
import VideoItem from "./VideoItem";
import { BigButton } from "components/CenteredPageComponents";
import { useConfig } from "config";

type WelcomeStepProps = {
  onSubmit: () => void;
  userName?: string;
};

const Videos = styled.div`
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: ${({ theme }) => theme.lightTextColor};
  font-size: 16px;
  margin: 20px 0 67px;
`;

const WelcomeStep: React.FC<WelcomeStepProps> = ({ userName, onSubmit }) => {
  const config = useConfig();

  return (
    <>
      <TitlesBlock
        testId="onboarding.welcome"
        title={
          userName ? (
            <FormattedMessage
              id="onboarding.welcomeUser"
              values={{ name: <HighlightedText>{userName}</HighlightedText> }}
            />
          ) : (
            <FormattedMessage id="onboarding.welcome" />
          )
        }
      >
        <FormattedMessage
          id="onboarding.welcomeUser.text"
          values={{
            b: (...b: React.ReactNode[]) => (
              <>
                <b>{b}</b>
                <br />
              </>
            ),
          }}
        />
      </TitlesBlock>
      <Videos>
        <VideoItem
          description={<FormattedMessage id="onboarding.watchVideo" />}
          videoId="sKDviQrOAbU"
          img="/videoCover.png"
        />
        <FormattedMessage id="onboarding.or" />
        <VideoItem
          description={<FormattedMessage id="onboarding.exploreDemo" />}
          img="/videoCover.png"
          link={config.ui.demoLink}
        />
      </Videos>
      <BigButton onClick={onSubmit} shadow>
        <FormattedMessage id="onboarding.firstConnection" />
      </BigButton>
    </>
  );
};

export default WelcomeStep;
