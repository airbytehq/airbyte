import React from "react";
import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCheck, faTimes, faBan, faExclamationTriangle } from "@fortawesome/free-solid-svg-icons";

import PauseIcon from "./PauseIcon";

interface Props {
  success?: boolean;
  warning?: boolean;
  title?: string;
  inactive?: boolean;
  empty?: boolean;
  className?: string;
  big?: boolean;
  value?: string | number;
}

const getBadgeWidth = (props: Props) => (props.big ? (props.value ? 57 : 40) : props.value ? 37 : 20);

const Badge = styled.div<Props>`
  width: ${(props) => getBadgeWidth(props)}px;
  height: ${({ big }) => (big ? 40 : 20)}px;
  background: ${(props) =>
    props.success
      ? props.theme.successColor
      : props.inactive
      ? props.theme.lightTextColor
      : props.empty
      ? props.theme.attentionColor
      : props.warning
      ? props.theme.warningColor
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

const StatusIcon: React.FC<Props> = ({ title, ...props }) => {
  return (
    <Badge {...props}>
      {props.success ? (
        <FontAwesomeIcon icon={faCheck} title={title} />
      ) : props.inactive ? (
        <PauseIcon title={title} />
      ) : props.empty ? (
        <FontAwesomeIcon icon={faBan} title={title} />
      ) : props.warning ? (
        <FontAwesomeIcon icon={faExclamationTriangle} title={title} />
      ) : (
        <FontAwesomeIcon icon={faTimes} title={title} />
      )}
      {props.value && <Value>{props.value}</Value>}
    </Badge>
  );
};

export default StatusIcon;
