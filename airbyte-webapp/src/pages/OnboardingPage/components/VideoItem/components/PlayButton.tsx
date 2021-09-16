import React from "react";
import styled, { keyframes } from "styled-components";

type PlayButtonProps = {
  small?: boolean;
  onClick: () => void;
};

export const BigCircleAnimation = keyframes`
  0% {
    height: 80%;
    width: 80%;
  }
  100% {
    width: 100%;
    height: 100%;
  }
`;

export const MiddleCircleAnimation = keyframes`
  0% {
    height: 53%;
    width: 53%;
  }
  100% {
    width: 73%;
    height: 73%;
  }
`;

export const SmallCircleAnimation = keyframes`
  0% {
    height: 20%;
    width: 20%;
  }
  100% {
    width: 40%;
    height: 40%;
  }
`;

const MainCircle = styled.div<PlayButtonProps>`
  cursor: pointer;
  height: ${({ small }) => (small ? 42 : 85)}px;
  width: ${({ small }) => (small ? 42 : 85)}px;
  border-radius: 50%;
  background: ${({ theme }) => theme.primaryColor};
  padding: ${({ small }) => (small ? "10px 0 0 16px" : "20px 0 0 32px")};
  box-shadow: 0 2.4px 4.8px ${({ theme }) => theme.cardShadowColor},
    0 16.2px 7.2px -10.2px ${({ theme }) => theme.cardShadowColor};

  &:hover {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 0;

    & > img {
      display: none;
    }
    & div {
      display: flex;
      justify-content: center;
      align-items: center;
    }
  }
`;

const BigCircle = styled.div<{ small?: boolean }>`
  height: ${({ small }) => (small ? 32 : 65)}px;
  width: ${({ small }) => (small ? 32 : 65)}px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.5);
  display: none;
  animation: ${BigCircleAnimation} alternate 0.5s linear 0s infinite;
`;

const MiddleCircle = styled(BigCircle)`
  height: ${({ small }) => (small ? 22 : 45)}px;
  width: ${({ small }) => (small ? 22 : 45)}px;
  animation-name: ${MiddleCircleAnimation};
`;

const SmallCircle = styled(BigCircle)`
  height: ${({ small }) => (small ? 8 : 17)}px;
  width: ${({ small }) => (small ? 8 : 17)}px;
  animation-name: ${SmallCircleAnimation};
`;

const PlayButton: React.FC<PlayButtonProps> = ({ small, onClick }) => {
  return (
    <MainCircle small={small} onClick={onClick}>
      <img src="/play.svg" height={small ? 22 : 44} alt="play" />
      <BigCircle>
        <MiddleCircle>
          <SmallCircle />
        </MiddleCircle>
      </BigCircle>
    </MainCircle>
  );
};

export default PlayButton;
