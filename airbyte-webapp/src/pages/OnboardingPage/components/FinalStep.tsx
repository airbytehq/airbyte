import React, { useEffect, useState } from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";
import { useResource, useSubscription } from "rest-hooks";

import VideoItem from "./VideoItem";
import ProgressBlock from "./ProgressBlock";
import HighlightedText from "./HighlightedText";
import { H1, Button } from "components/base";
import UseCaseBlock from "./UseCaseBlock";
import ConnectionResource from "core/resources/Connection";
import SyncCompletedModal from "views/Feedback/SyncCompletedModal";
import { useOnboardingService } from "hooks/services/Onboarding/OnboardingService";
import Status from "core/statuses";
import useWorkspace from "hooks/services/useWorkspace";

type FinalStepProps = {
  connectionId: string;
  onSync: () => void;
  onFinishOnboarding: () => void;
};

const Title = styled(H1)`
  margin: 21px 0;
`;

const Videos = styled.div`
  width: 425px;
  height: 205px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 20px 0 50px;
  background: url("/video-background.svg") no-repeat;
  padding: 0 27px;
`;

const CloseButton = styled(Button)`
  margin-top: 30px;
`;

const FinalStep: React.FC<FinalStepProps> = ({
  connectionId,
  onSync,
  onFinishOnboarding,
}) => {
  const { sendFeedback } = useWorkspace();
  const {
    feedbackPassed,
    passFeedback,
    useCases,
    skipCase,
  } = useOnboardingService();
  const connection = useResource(ConnectionResource.detailShape(), {
    connectionId,
  });
  useSubscription(ConnectionResource.detailShape(), {
    connectionId: connectionId,
  });
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    if (
      connection.latestSyncJobStatus === Status.SUCCEEDED &&
      !feedbackPassed
    ) {
      setIsOpen(true);
    }
  }, [connection.latestSyncJobStatus, feedbackPassed]);

  const onSendFeedback = (feedback: string) => {
    sendFeedback({
      feedback,
      source: connection.source,
      destination: connection.destination,
    });
    passFeedback();
    setIsOpen(false);
  };

  return (
    <>
      <Videos>
        <VideoItem
          small
          description={<FormattedMessage id="onboarding.watchVideo" />}
          videoId="sKDviQrOAbU"
          img="/videoCover.png"
        />
        <VideoItem
          small
          description={<FormattedMessage id="onboarding.exploreDemo" />}
          videoId="sKDviQrOAbU"
          img="/videoCover.png"
        />
      </Videos>
      {!feedbackPassed && (
        <ProgressBlock connection={connection} onSync={onSync} />
      )}

      <Title bold>
        <FormattedMessage
          id="onboarding.useCases"
          values={{
            name: (...name: React.ReactNode[]) => (
              <HighlightedText>{name}</HighlightedText>
            ),
          }}
        />
      </Title>

      {useCases &&
        useCases.map((item, key) => (
          <UseCaseBlock
            key={item}
            count={key + 1}
            onSkip={skipCase}
            id={item}
          />
        ))}

      <CloseButton secondary onClick={onFinishOnboarding}>
        <FormattedMessage id="onboarding.closeOnboarding" />
      </CloseButton>

      {isOpen ? (
        <SyncCompletedModal
          onClose={() => setIsOpen(false)}
          onPassFeedback={onSendFeedback}
        />
      ) : null}
    </>
  );
};

export default FinalStep;
