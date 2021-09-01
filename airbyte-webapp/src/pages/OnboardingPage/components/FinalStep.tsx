import React from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";

import VideoItem from "./VideoItem";
import ProgressBlock from "./ProgressBlock";
import HighlightedText from "./HighlightedText";
import { H1, Button } from "components/base";
import UseCaseBlock from "./UseCaseBlock";

type FinalStepProps = {
  useCases?: { id: string; data: React.ReactNode }[];
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

const FinalStep: React.FC<FinalStepProps> = ({ useCases }) => {
  return (
    <>
      <Videos>
        <VideoItem
          small
          description={<FormattedMessage id="onboarding.watchVideo" />}
        />
        <VideoItem
          small
          description={<FormattedMessage id="onboarding.exploreDemo" />}
        />
      </Videos>
      <ProgressBlock />
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
          <UseCaseBlock key={item.id} count={key + 1}>
            {item.data}
          </UseCaseBlock>
        ))}

      <CloseButton secondary>
        <FormattedMessage id="onboarding.closeOnboarding" />
      </CloseButton>
    </>
  );
};

export default FinalStep;
