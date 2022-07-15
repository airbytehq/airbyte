import { faTimes } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import styled, { keyframes } from "styled-components";

import { Button, H5 } from "components";

import ErrorSign from "./components/ErrorSign";

interface SingletonCardProps {
  title: string | React.ReactNode;
  text?: string | React.ReactNode;
  hasError?: boolean;
  onClose?: () => void;
}

export const SlideUpAnimation = keyframes`
  0% {
    translate(-50%, -100%);
    bottom: -49px;
  }
  100% {
    translate(-50%, 0);
    bottom: 49px;
  }
`;

const Singleton = styled.div<{ hasError?: boolean }>`
  position: fixed;
  bottom: 49px;
  left: 50%;
  transform: translate(-50%, 0);
  z-index: 20;

  padding: 25px 25px 22px;

  background: ${({ theme, hasError }) => (hasError ? theme.lightDangerColor : theme.lightPrimaryColor)};
  border: 1px solid ${({ theme }) => theme.greyColor20};
  box-shadow: 0 1px 2px ${({ theme }) => theme.shadowColor};
  border-radius: 8px;

  display: flex;
  flex-direction: row;
  align-items: center;

  animation: ${SlideUpAnimation} 0.25s linear;
`;

const Title = styled(H5)<{ hasError?: boolean }>`
  color: ${({ theme, hasError }) => (hasError ? theme.dangerColor : theme.primaryColor)};

  font-style: normal;
  font-weight: bold;
  font-size: 15px;
  line-height: 18px;
`;

const Text = styled.div`
  color: ${({ theme }) => theme.mediumPrimaryColor};

  font-style: normal;
  font-weight: normal;
  font-size: 14px;
  line-height: 17px;
  margin-top: 5px;
`;

const CloseButton = styled(Button)`
  margin-left: 10px;
`;

const SingletonCard: React.FC<SingletonCardProps> = (props) => (
  <Singleton hasError={props.hasError}>
    {props.hasError && <ErrorSign />}
    <div>
      <Title hasError={props.hasError}>{props.title}</Title>
      {props.text && <Text>{props.text}</Text>}
    </div>
    {props.onClose && (
      <CloseButton iconOnly onClick={props.onClose}>
        <FontAwesomeIcon icon={faTimes} />
      </CloseButton>
    )}
  </Singleton>
);

export default SingletonCard;
