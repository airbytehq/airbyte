import React from "react";
import styled from "styled-components";

type ToolTipProps = {
  control: React.ReactNode;
};

const Control = styled.div`
  display: inline-block;
  position: relative;
  cursor: pointer;
`;

const ToolTipView = styled.div`
  display: none;
  position: absolute;
  padding: 9px 8px 8px;
  box-shadow: 0 24px 38px rgba(53, 53, 66, 0.14),
    0 9px 46px rgba(53, 53, 66, 0.12), 0 11px 15px rgba(53, 53, 66, 0.2);
  border-radius: 4px;
  background: rgba(26, 26, 33, 0.9);
  top: calc(100% + 10px);
  left: -50px;
  min-width: 100px;

  div:hover > & {
    display: block;
  }
`;

const ToolTip: React.FC<ToolTipProps> = ({ children, control }) => {
  return (
    <Control>
      {control}
      <ToolTipView>{children}</ToolTipView>
    </Control>
  );
};

export default ToolTip;
