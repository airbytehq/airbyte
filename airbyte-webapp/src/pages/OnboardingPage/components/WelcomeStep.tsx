import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button } from "components";
import { useExperimentSpeedyConnection } from "components/experiments/SpeedyConnection/hooks/useExperimentSpeedyConnection";

import { useConfig } from "config";
import { Action, Namespace } from "core/analytics";
import { useAnalyticsService } from "hooks/services/Analytics";

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
  // exp-speedy-connection
  const { isExperimentVariant } = useExperimentSpeedyConnection();
  const analyticsService = useAnalyticsService();

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

      <Button
        size="lg"
        onClick={() => {
          // exp-speedy-connection
          if (isExperimentVariant) {
            analyticsService.track(Namespace.ONBOARDING, Action.START_EXP_SPEEDY_CONNECTION, {
              actionDescription: "Start Onboarding speedy connection experiment",
            });
          }
          onNextStep();
        }}
      >
        <FormattedMessage id="onboarding.firstConnection" />
      </Button>
    </>
  );
};

export default WelcomeStep;
