import React from "react";
import styled from "styled-components";
import Spinner from "../Spinner";
import { theme } from "../../theme";

type IProps = {
  full?: boolean;
};

const Container = styled.div<IProps>`
  width: 100%;
  height: ${({ full }) => (full ? "100%" : "auto")};
  padding: 20px 10px;
  display: flex;
  justify-content: center;
  align-items: center;
`;

const LoadingPage: React.FC<IProps> = ({ full }) => (
  <Container full={full}>
    <Spinner backgroundColor={theme.greyColor0} />
  </Container>
);

export default LoadingPage;
