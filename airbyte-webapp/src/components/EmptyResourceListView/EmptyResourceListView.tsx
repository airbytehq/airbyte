import { useMemo } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

// import { H2 } from "components/base";
import { BigButton } from "components/CenteredPageComponents";
import HeadTitle from "components/HeadTitle";

import TitlesBlock from "pages/OnboardingPage/components/TitlesBlock";

interface EmptyResourceListViewProps {
  resourceType: "connections" | "destinations" | "sources";
  onCreateClick: () => void;
  disableCreateButton?: boolean;
}

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  background-color: #212946;
`;

// const Heading = styled(H2)`
//   font-weight: 700;
//   font-size: 24px;
//   line-height: 29px;
//   max-width: 386px;
//   text-align: center;
//   strong {
//     color: ${({ theme }) => theme.redColor};
//   }
// `;

const IllustrationContainer = styled(Container)`
  position: relative;
  width: 700px;
  height: 276px;

  pointer-events: none;
  user-select: none;
  display: flex;
  justify-content: center;
  align-items: center;
  color: ${({ theme }) => theme.lightTextColor};
  margin-top: 50px;
`;

// const OctaviaImg = styled.img`
//   max-height: 203px;
//   max-width: 100%;
//   z-index: 1;
// `;

// const BowtieImg = styled.img`
//   position: absolute;

//   &.empty-list-bowtie--right {
//     right: 0;
//     transform: scaleX(-1);
//   }

//   &.empty-list-bowtie--left {
//     left: 0;
//   }
// `;

const ButtonContainer = styled.div`
  padding: 18px;
  background-color: #2a2f66;
  border-radius: 60px;
  margin: 70px 0 50px 0;
`;

export const EmptyResourceListView: React.FC<EmptyResourceListViewProps> = ({
  resourceType,
  onCreateClick,
  // disableCreateButton,
}) => {
  const {
    // headingMessageId,
    // buttonMessageId,
    // singularResourceType
  } = useMemo(() => {
    const singularResourceType = resourceType.substring(0, resourceType.length - 1);
    const baseMessageId = resourceType === "connections" ? singularResourceType : resourceType;

    const headingMessageId = `${baseMessageId}.description`;
    const buttonMessageId = `${baseMessageId}.new${
      singularResourceType.substring(0, 1).toUpperCase() + singularResourceType.substring(1)
    }`;

    return { headingMessageId, buttonMessageId, singularResourceType };
  }, [resourceType]);

  const getPageTitle = (resourceType: "connections" | "destinations" | "sources"): string => {
    switch (resourceType) {
      case "connections":
        return "admin.dashboard";

      case "sources":
        return "admin.sources";

      case "destinations":
        return "admin.destinations";

      default:
        return "admin.dashboard";
    }
  };

  return (
    <Container>
      <HeadTitle titles={[{ id: getPageTitle(resourceType) }]} />
      {/* <Heading>
        <FormattedMessage id={headingMessageId} />
      </Heading> */}
      <TitlesBlock testId="onboarding.welcome" title={<FormattedMessage id="onboarding.welcome" />}>
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
      <IllustrationContainer>
        {/* {resourceType !== "destinations" && (
          <BowtieImg src="/images/bowtie-half.svg" alt="Left Bowtie" className="empty-list-bowtie--left" />
        )}
        {resourceType !== "sources" && (
          <BowtieImg src="/images/bowtie-half.svg" alt="Right Bowtie" className="empty-list-bowtie--right" />
        )}
        <OctaviaImg src={`/images/octavia/empty-${resourceType}.png`} alt="Octavia" resource={resourceType} /> */}
        <img src="/daspireDashboard.png" alt="logo" style={{ maxWidth: "100%", height: "auto", objectFit: "cover" }} />
      </IllustrationContainer>
      <ButtonContainer>
        <BigButton shadow onClick={onCreateClick}>
          <FormattedMessage id="onboarding.firstConnection" />
        </BigButton>
      </ButtonContainer>
      {/* <Button onClick={onCreateClick} disabled={disableCreateButton} size="xl" data-id={`new-${singularResourceType}`}>
        <FormattedMessage id={buttonMessageId} />
      </Button> */}
    </Container>
  );
};
