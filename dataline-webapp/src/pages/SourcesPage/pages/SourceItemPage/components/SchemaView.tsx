import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import ContentCard from "../../../../../components/ContentCard";
import Button from "../../../../../components/Button";

const Content = styled.div`
  max-width: 806px;
  margin: 18px auto;
`;

const ButtonsContainer = styled.div`
  text-align: right;
  margin-bottom: 16px;
`;

const SaveButton = styled(Button)`
  margin-left: 11px;
`;

const SchemaView: React.FC = () => {
  return (
    <Content>
      <ButtonsContainer>
        <Button secondary disabled>
          <FormattedMessage id={"form.discardChanges"} />
        </Button>
        <SaveButton disabled>
          <FormattedMessage id={"form.saveChanges"} />
        </SaveButton>
      </ButtonsContainer>
      <ContentCard>SCHEMA</ContentCard>
    </Content>
  );
};

export default SchemaView;
