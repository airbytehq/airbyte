import React from "react";
import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCheck, faTimes, faBan } from "@fortawesome/free-solid-svg-icons";

import PauseIcon from "./components/Pause";

type IProps = {
  success?: boolean;
  title?: string;
  inactive?: boolean;
  empty?: boolean;
  className?: string;
  big?: boolean;
  value?: string | number;
};

const getWidth = (props: IProps) => {
  if (props.big) {
    return props.value ? 57 : 40;
  }

  return props.value ? 37 : 20;
};

const Badge = styled.div<IProps>`
  width: ${(props) => getWidth(props)}px;
  height: ${({ big }) => (big ? 40 : 20)}px;
  background: ${(props) =>
    props.success
      ? props.theme.successColor
      : props.inactive
      ? props.theme.lightTextColor
      : props.empty
      ? props.theme.attentionColor
      : props.theme.dangerColor};
  box-shadow: 0 1px 2px ${({ theme }) => theme.shadowColor};
  border-radius: ${({ value }) => (value ? "15px" : "50%")};
  margin-right: 10px;
  padding-top: 4px;
  color: ${({ theme }) => theme.whiteColor};
  font-size: ${({ big }) => (big ? 24 : 12)}px;
  line-height: ${({ big }) => (big ? 33 : 12)}px;
  text-align: center;
  display: inline-block;
  vertical-align: top;
`;

const Value = styled.span`
  font-weight: 500;
  font-size: 12px;
  padding-left: 3px;
  vertical-align: top;
`;

const StatusIcon: React.FC<IProps> = (props) => (
  <Badge {...props}>
    {props.success ? (
      <FontAwesomeIcon icon={faCheck} title={props.title} />
    ) : props.inactive ? (
      <PauseIcon />
    ) : props.empty ? (
      <FontAwesomeIcon icon={faBan} title={props.title} />
    ) : (
      <FontAwesomeIcon icon={faTimes} title={props.title} />
    )}
    {props.value && <Value>{props.value}</Value>}
  </Badge>
);

export default StatusIcon;
