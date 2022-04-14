import React from "react";
import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCheck, faTimes, faBan, faExclamationTriangle, IconDefinition } from "@fortawesome/free-solid-svg-icons";

import PauseIcon from "./PauseIcon";

export type StatusIconStatus = "empty" | "inactive" | "success" | "warning";

interface Props {
  className?: string;
  status?: StatusIconStatus;
  title?: string;
  big?: boolean;
  value?: string | number;
}

const getBadgeWidth = (props: Props) => (props.big ? (props.value ? 57 : 40) : props.value ? 37 : 20);

const _iconByStatus: Record<StatusIconStatus, IconDefinition | undefined> = {
  empty: faBan,
  inactive: undefined,
  success: faCheck,
  warning: faExclamationTriangle,
};

const _themeByStatus: Record<StatusIconStatus, string> = {
  empty: "attentionColor",
  inactive: "lightTextColor",
  success: "successColor",
  warning: "warningColor",
};

const Badge = styled.div<Props>`
  width: ${(props) => getBadgeWidth(props)}px;
  height: ${({ big }) => (big ? 40 : 20)}px;
  background: ${(props) => props.theme[(props.status && _themeByStatus[props.status]) || "dangerColor"]};
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

const StatusIcon: React.FC<Props> = ({ title, status, ...props }) => {
  return (
    <Badge {...props} status={status}>
      {status === "inactive" ? (
        <PauseIcon title={title} />
      ) : (
        <FontAwesomeIcon icon={(status && _iconByStatus[status]) || faTimes} title={title} />
      )}
      {props.value && <Value>{props.value}</Value>}
    </Badge>
  );
};

export default StatusIcon;
