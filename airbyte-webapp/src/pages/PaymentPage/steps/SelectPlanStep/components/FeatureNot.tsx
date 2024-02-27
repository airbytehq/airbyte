import { Box } from "@mui/material";
import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

const Title = styled.div`
  font-weight: 500;
  font-size: 18px;
  line-height: 30px;
  color: ${({ theme }) => theme.black300};
  user-select: none;
`;

const CardContainer = styled.div`
  padding: 20px 20px;
  background: #ffffff;
  border-radius: 16px;
`;

const FeatureNot: React.FC = () => {
  return (
    <CardContainer>
      <Box display="flex" justifyContent="center" alignItems="center" pl={1}>
        <Title>
          <FormattedMessage id="plan.type.instancenot" />
        </Title>
      </Box>
    </CardContainer>
  );
};

export default FeatureNot;
