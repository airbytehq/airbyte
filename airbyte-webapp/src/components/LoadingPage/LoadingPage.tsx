import React from "react";
import styled, { useTheme } from "styled-components";
import Spinner from "components/Spinner";
import { Theme } from "theme";

type IProps = {
  full?: boolean;
};

const Container = styled.div<IProps>`
  width: 100%;
  height: 100%;
  padding: 20px 10px;
  display: flex;
  justify-content: center;
  align-items: center;
`;

const LoadingPage: React.FC<IProps> = ({ full }) => {
  const theme = useTheme() as Theme;
  return (
    <Container full={full}>
      <Spinner backgroundColor={theme.backgroundColor} />
    </Container>
  );
};

export default LoadingPage;
