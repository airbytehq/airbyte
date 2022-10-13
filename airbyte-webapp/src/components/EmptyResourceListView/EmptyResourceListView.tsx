import { useMemo } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button, H2 } from "components/base";

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
`;

const Heading = styled(H2)`
  font-weight: 700;
  font-size: 24px;
  line-height: 29px;
  max-width: 386px;
  text-align: center;
  strong {
    color: ${({ theme }) => theme.redColor};
  }
`;

const IllustrationContainer = styled(Container)`
  position: relative;
  width: 592px;
  height: 276px;

  pointer-events: none;
  user-select: none;
`;

const OctaviaImg = styled.img`
  max-height: 203px;
  max-width: 100%;
  z-index: 1;
`;

const BowtieImg = styled.img`
  position: absolute;

  &.empty-list-bowtie--right {
    right: 0;
    transform: scaleX(-1);
  }

  &.empty-list-bowtie--left {
    left: 0;
  }
`;

export const EmptyResourceListView: React.FC<EmptyResourceListViewProps> = ({
  resourceType,
  onCreateClick,
  disableCreateButton,
}) => {
  const { headingMessageId, buttonMessageId, singularResourceType } = useMemo(() => {
    const singularResourceType = resourceType.substring(0, resourceType.length - 1);
    const baseMessageId = resourceType === "connections" ? singularResourceType : resourceType;

    const headingMessageId = `${baseMessageId}.description`;
    const buttonMessageId = `${baseMessageId}.new${
      singularResourceType.substring(0, 1).toUpperCase() + singularResourceType.substring(1)
    }`;

    return { headingMessageId, buttonMessageId, singularResourceType };
  }, [resourceType]);

  return (
    <Container>
      <Heading>
        <FormattedMessage id={headingMessageId} />
      </Heading>
      <IllustrationContainer>
        {resourceType !== "destinations" && (
          <BowtieImg src="/images/bowtie-half.svg" alt="Left Bowtie" className="empty-list-bowtie--left" />
        )}
        {resourceType !== "sources" && (
          <BowtieImg src="/images/bowtie-half.svg" alt="Right Bowtie" className="empty-list-bowtie--right" />
        )}
        <OctaviaImg src={`/images/octavia/empty-${resourceType}.png`} alt="Octavia" resource={resourceType} />
      </IllustrationContainer>
      <Button onClick={onCreateClick} disabled={disableCreateButton} size="xl" data-id={`new-${singularResourceType}`}>
        <FormattedMessage id={buttonMessageId} />
      </Button>
    </Container>
  );
};
