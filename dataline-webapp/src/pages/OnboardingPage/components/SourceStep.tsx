import React from "react";
import { FormattedMessage } from "react-intl";

import ContentCard from "../../../components/ContentCard";
import Button from "../../../components/Button";
import { FormContainer, ButtonContainer } from "./FormComponents";

type IProps = {
  onSubmit: () => void;
};

const SourceStep: React.FC<IProps> = ({ onSubmit }) => {
  return (
    <ContentCard title={<FormattedMessage id="onboarding.setUpSource" />}>
      <FormContainer>
        <ButtonContainer>
          <Button onClick={onSubmit}>
            <FormattedMessage id="onboarding.setUpSource.buttonText" />
          </Button>
        </ButtonContainer>
      </FormContainer>
    </ContentCard>
  );
};

export default SourceStep;
