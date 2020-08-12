import React from "react";
import { FormattedMessage } from "react-intl";

import ContentCard from "../../../components/ContentCard";
import Button from "../../../components/Button";
import { FormContainer, ButtonContainer } from "./FormComponents";

type IProps = {
  onSubmit: () => void;
};

const Destination: React.FC<IProps> = ({ onSubmit }) => {
  return (
    <ContentCard title={<FormattedMessage id="onboarding.setUpDestination" />}>
      <FormContainer>
        <ButtonContainer>
          <Button onClick={onSubmit}>
            <FormattedMessage id="onboarding.setUpDestination.buttonText" />
          </Button>
        </ButtonContainer>
      </FormContainer>
    </ContentCard>
  );
};

export default Destination;
