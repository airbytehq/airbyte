import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { BigButton } from "components/CenteredPageComponents";

// import { useConfig } from "config";

// import HighlightedText from "./HighlightedText";
import useRouter from "hooks/useRouter";
import { RoutePaths } from "pages/routePaths";

import TitlesBlock from "./TitlesBlock";
// import VideoItem from "./VideoItem";

interface WelcomeStepProps {
  onNextStep: () => void;
  userName?: string;
}

const ImageContainer = styled.div`
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  color: ${({ theme }) => theme.lightTextColor};
  font-size: 16px;
`;

const ButtonContainer = styled.div`
  padding: 18px;
  background-color: #2a2f66;
  border-radius: 60px;
`;

// const Videos = styled.div`
//   width: 100%;
//   display: flex;
//   justify-content: space-between;
//   align-items: center;
//   color: ${({ theme }) => theme.lightTextColor};
//   font-size: 16px;
//   margin: 20px 0 67px;
// `;
// { onNextStep }
const WelcomeStep: React.FC<WelcomeStepProps> = () => {
  // const config = useConfig();
  const { push } = useRouter();

  const onCreateClick = () => push(`${RoutePaths.ConnectionNew}`);

  return (
    <>
      <TitlesBlock
        testId="onboarding.welcome"
        title={
          // userName ? (
          //   <FormattedMessage
          //     id="onboarding.welcomeUser"
          //     values={{ name: <HighlightedText>{userName}</HighlightedText> }}
          //   />
          // ) : (
          <FormattedMessage id="onboarding.welcome" />
          // )
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
      <ImageContainer>
        <img src="/daspireDashboard.png" alt="logo" style={{ maxWidth: "100%", height: "auto", objectFit: "cover" }} />
      </ImageContainer>
      {/* <Videos>*/}
      {/*  <VideoItem*/}
      {/*    description={<FormattedMessage id="onboarding.watchVideo" />}*/}
      {/*    videoId="sKDviQrOAbU"*/}
      {/*    img="/videoCover.png"*/}
      {/*  />*/}
      {/*  <FormattedMessage id="onboarding.or" />*/}
      {/*  <VideoItem*/}
      {/*    description={<FormattedMessage id="onboarding.exploreDemo" />}*/}
      {/*    img="/videoCover.png"*/}
      {/*    link={config.links.demoLink}*/}
      {/*  />*/}
      {/* </Videos>*/}
      <ButtonContainer>
        {/* onClick={onNextStep}*/}
        <BigButton shadow onClick={onCreateClick}>
          <FormattedMessage id="onboarding.firstConnection" />
        </BigButton>
      </ButtonContainer>
    </>
  );
};

export default WelcomeStep;
