import React from "react";
import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCheck, faTimes } from "@fortawesome/free-solid-svg-icons";

type IProps = {
  success?: boolean;
  className?: string;
  big?: boolean;
};

const Badge = styled.div<IProps>`
  width: ${({ big }) => (big ? 40 : 20)}px;
  height: ${({ big }) => (big ? 40 : 20)}px;
  background: ${(props) =>
    props.success ? props.theme.successColor : props.theme.dangerColor};
  box-shadow: 0 1px 2px ${({ theme }) => theme.shadowColor};
  border-radius: 50%;
  margin-right: 10px;
  padding-top: 4px;
  color: ${({ theme }) => theme.whiteColor};
  font-size: ${({ big }) => (big ? 24 : 12)}px;
  line-height: ${({ big }) => (big ? 33 : 12)}px;
  text-align: center;
  display: inline-block;
`;

const StatusIcon: React.FC<IProps> = ({ success, className, big }) => (
  <Badge success={success} className={className} big={big}>
    {success ? (
      <FontAwesomeIcon icon={faCheck} />
    ) : (
      <FontAwesomeIcon icon={faTimes} />
    )}
  </Badge>
);

export default StatusIcon;
