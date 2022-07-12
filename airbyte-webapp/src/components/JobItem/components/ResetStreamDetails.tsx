import React from "react";
import styled from "styled-components";

interface IProps {
  names: string[];
}

const Container = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
  margin-top: 4px;
`;

const BadgeContainer = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  height: 20px;
  padding: 0 5px;
  background: #f8f8fa;
  border: 1px solid #e8e8ed;
  border-radius: 4px;
`;

const BadgeText = styled.p`
  font-weight: 400;
  font-size: 12px;
  line-height: 15px;
  color: #8b8ba0;
`;

export const ResetStreamsDetails: React.FC<IProps> = ({ names }) => (
  <Container>
    {names.map((name) => (
      <BadgeContainer>
        <BadgeText>{name}</BadgeText>
      </BadgeContainer>
    ))}
  </Container>
);
