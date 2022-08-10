import React from "react";
import styled from "styled-components";

interface ToolTipProps {
  control: React.ReactNode;
  className?: string;
  disabled?: boolean;
  cursor?: "pointer" | "help" | "not-allowed";
}

const Control = styled.div<{ $cursor?: "pointer" | "help" | "not-allowed"; $showCursor?: boolean }>`
  display: inline;
  position: relative;
  ${({ $cursor, $showCursor = true }) => ($showCursor && $cursor ? `cursor: ${$cursor}` : "")};
`;

const ToolTipView = styled.div<{ $disabled?: boolean }>`
  display: none;
  font-size: 14px;
  line-height: initial;
  position: absolute;
  padding: 9px 8px 8px;
  box-shadow: 0 24px 38px rgba(53, 53, 66, 0.14), 0 9px 46px rgba(53, 53, 66, 0.12), 0 11px 15px rgba(53, 53, 66, 0.2);
  border-radius: 4px;
  background: rgba(26, 26, 33, 0.9);
  color: ${({ theme }) => theme.whiteColor};
  top: calc(100% + 10px);
  left: -50px;
  min-width: 100px;
  width: max-content;
  max-width: 380px;
  z-index: 10;

  div:hover > &&,
  &&:hover {
    display: ${({ $disabled }) => ($disabled ? "none" : "block")};
  }
`;

const ToolTip: React.FC<ToolTipProps> = ({ children, control, className, disabled, cursor }) => {
  return (
    <Control $cursor={cursor} $showCursor={!disabled}>
      {control}
      <ToolTipView className={className} $disabled={disabled}>
        {children}
      </ToolTipView>
    </Control>
  );
};

export default ToolTip;
