import React from "react";
import styled from "styled-components";

import Spinner from "components/Spinner";

interface IProps {
  full?: boolean;
}

const Container = styled.div<IProps>`
  width: 100%;
  height: 100%;
  padding: 20px 10px;
  display: flex;
  justify-content: center;
  align-items: center;
`;

const LoadingPage: React.FC<IProps> = ({ full }) => (
  <Container full={full}>
    <Spinner />
  </Container>
);

export default LoadingPage;
