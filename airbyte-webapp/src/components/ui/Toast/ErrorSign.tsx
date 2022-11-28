import { faExclamation } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import styled from "styled-components";

const ErrorIcon = styled.div`
  width: 28px;
  min-width: 28px;
  height: 28px;
  border-radius: 50%;
  margin-right: 11px;
  display: flex;
  justify-content: center;
  align-items: center;
  background: ${({ theme }) => theme.dangerColor};
  border: 1px solid ${({ theme }) => theme.mediumPrimaryColor20};
`;

const ExclamationLight = styled(FontAwesomeIcon)`
  font-size: 16px;
  color: ${({ theme }) => theme.whiteColor};
`;

export const ErrorSign: React.FC = () => (
  <ErrorIcon>
    <ExclamationLight icon={faExclamation} />
  </ErrorIcon>
);
