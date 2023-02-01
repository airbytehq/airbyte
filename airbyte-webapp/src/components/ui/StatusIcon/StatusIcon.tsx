import { faBan, faCheck, faExclamationTriangle, faMinus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import styled from "styled-components";

import { CrossIcon } from "components/icons/CrossIcon";
import { MoonIcon } from "components/icons/MoonIcon";
import { PauseIcon } from "components/icons/PauseIcon";

import { CircleLoader } from "./CircleLoader";

export type StatusIconStatus = "sleep" | "inactive" | "success" | "warning" | "loading" | "error" | "cancelled";

interface StatusIconProps {
  className?: string;
  status?: StatusIconStatus;
  title?: string;
  big?: boolean;
  value?: string | number;
}

const getBadgeWidth = (props: StatusIconProps) => (props.big ? (props.value ? 57 : 40) : props.value ? 37 : 20);

const _iconByStatus = {
  sleep: faBan,
  success: faCheck,
  warning: faExclamationTriangle,
  cancelled: faMinus,
} as const;

const _themeByStatus = {
  sleep: "lightTextColor",
  inactive: "lightTextColor",
  success: "successColor",
  warning: "warningColor",
  error: "dangerColor",
  cancelled: "lightTextColor",
} as const;

const Container = styled.div<Pick<StatusIconProps, "big" | "value">>`
  width: ${(props) => getBadgeWidth(props)}px;
  height: ${({ big }) => (big ? 40 : 20)}px;
  margin-right: 10px;
  font-size: ${({ big }) => (big ? 24 : 12)}px;
  line-height: ${({ big }) => (big ? 33 : 12)}px;
  text-align: center;
  display: inline-block;
  vertical-align: middle;
`;

const Badge = styled(Container)<{ status: Exclude<StatusIconStatus, "loading"> }>`
  background: ${({ theme, status }) => theme[_themeByStatus[status]]};
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

export const StatusIcon: React.FC<StatusIconProps> = ({ title, status = "error", ...props }) => {
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
      ) : status === "error" ? (
        <CrossIcon title={title} />
      ) : (
        <FontAwesomeIcon icon={_iconByStatus[status]} title={title} />
      )}
      {valueElement}
    </Badge>
  );
};
