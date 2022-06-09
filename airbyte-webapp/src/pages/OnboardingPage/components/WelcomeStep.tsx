import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { BigButton } from "components/CenteredPageComponents";

import { useConfig } from "config";

import HighlightedText from "./HighlightedText";
import TitlesBlock from "./TitlesBlock";
import VideoItem from "./VideoItem";

interface WelcomeStepProps {
  onNextStep: () => void;
  userName?: string;
}

const Videos = styled.div`
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: ${({ theme }) => theme.lightTextColor};
  font-size: 16px;
  margin: 20px 0 67px;
`;

const WelcomeStep: React.FC<WelcomeStepProps> = ({ userName, onNextStep }) => {
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
            b: (b: React.ReactNode) => (
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
          link={config.links.demoLink}
        />
      </Videos>
      <BigButton onClick={onNextStep} shadow>
        <FormattedMessage id="onboarding.firstConnection" />
      </BigButton>
    </>
  );
};

export default WelcomeStep;
