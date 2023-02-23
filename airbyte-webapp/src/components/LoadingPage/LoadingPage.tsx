import React from "react";
import styled from "styled-components";

import Spinner from "components/Spinner";

interface IProps {
  full?: boolean;
  position?: string;
}

const Container = styled.div<IProps>`
  width: 100%;
  height: 100%;
  padding: 20px 10px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: ${({ theme, position }) => (position ? theme.backgroundColor : "transparent")};
  z-index: 10005;
  position: ${({ position }) => (position ? position : "static")};
`;

const LoadingPage: React.FC<IProps> = ({ full, position }) => (
  <Container full={full} position={position}>
    <Spinner />
  </Container>
);

export default LoadingPage;
