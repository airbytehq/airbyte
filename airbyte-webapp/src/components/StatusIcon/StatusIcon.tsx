import { faBan, faCheck, faExclamationTriangle, faTimes, IconDefinition } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import styled from "styled-components";

import { MoonIcon } from "components/icons/MoonIcon";

import PauseIcon from "../icons/PauseIcon";
import CircleLoader from "./CircleLoader";

export type StatusIconStatus = "sleep" | "inactive" | "success" | "warning" | "loading";

interface StatusIconProps {
  className?: string;
  status?: StatusIconStatus;
  title?: string;
  big?: boolean;
  value?: string | number;
}

const getBadgeWidth = (props: StatusIconProps) => (props.big ? (props.value ? 57 : 40) : props.value ? 37 : 20);

const _iconByStatus: Partial<Record<StatusIconStatus, IconDefinition | undefined>> = {
  sleep: faBan,
  success: faCheck,
  warning: faExclamationTriangle,
};

const _themeByStatus: Partial<Record<StatusIconStatus, string>> = {
  sleep: "lightTextColor",
  inactive: "lightTextColor",
  success: "successColor",
  warning: "warningColor",
};

const Container = styled.div<StatusIconProps>`
  width: ${(props) => getBadgeWidth(props)}px;
  height: ${({ big }) => (big ? 40 : 20)}px;
  margin-right: 10px;
  font-size: ${({ big }) => (big ? 24 : 12)}px;
  line-height: ${({ big }) => (big ? 33 : 12)}px;
  text-align: center;
  display: inline-block;
  vertical-align: middle;
`;

const Badge = styled(Container)<StatusIconProps>`
  background: ${(props) => props.theme[(props.status && _themeByStatus[props.status]) || "dangerColor"]};
  border-radius: ${({ value }) => (value ? "15px" : "50%")};
  color: ${({ theme }) => theme.whiteColor};
  padding-top: ${({ status }) => (status === "warning" || status === "inactive" ? 3 : 4)}px;

  > svg {
    height: 1em;
    vertical-align: -0.125em;
  }

  > span {
    vertical-align: ${({ status }) => (status === "inactive" ? "bottom" : "top")};
  }
`;

const Value = styled.span`
  font-weight: 500;
  font-size: 12px;
  padding-left: 3px;
`;

const StatusIcon: React.FC<StatusIconProps> = ({ title, status, ...props }) => {
  const valueElement = props.value ? <Value>{props.value}</Value> : null;

  if (status === "loading") {
    return (
      <Container>
        <CircleLoader title={title} />
        {valueElement}
      </Container>
    );
  }

  return (
    <Badge {...props} status={status}>
      {status === "inactive" ? (
        <PauseIcon title={title} />
      ) : status === "sleep" ? (
        <MoonIcon title={title} />
      ) : (
        <FontAwesomeIcon icon={(status && _iconByStatus[status]) || faTimes} title={title} />
      )}
      {valueElement}
    </Badge>
  );
};

export default StatusIcon;
