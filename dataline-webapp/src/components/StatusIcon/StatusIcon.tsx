import React from "react";
import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCheck, faTimes } from "@fortawesome/pro-regular-svg-icons";

type IProps = {
  success?: boolean;
  className?: string;
};

const Badge = styled.div<IProps>`
  width: 20px;
  height: 20px;
  background: ${props =>
    props.success ? props.theme.successColor : props.theme.dangerColor};
  box-shadow: 0 1px 2px ${({ theme }) => theme.shadowColor};
  border-radius: 50%;
  margin-right: 6px;
  padding-top: 2px;
  color: ${({ theme }) => theme.whiteColor};
  font-size: 14px;
  text-align: center;
  display: inline-block;
`;

const StatusIcon: React.FC<IProps> = ({ success, className }) => (
  <Badge success={success} className={className}>
    {success ? (
      <FontAwesomeIcon icon={faCheck} />
    ) : (
      <FontAwesomeIcon icon={faTimes} />
    )}
  </Badge>
);

export default StatusIcon;
