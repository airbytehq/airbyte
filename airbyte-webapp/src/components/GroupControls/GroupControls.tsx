import React from "react";
import styled from "styled-components";

import { Label, TextWithHTML } from "components";

const GroupTitle = styled.div<{ $fullWidthTitle: boolean }>`
  margin-top: -23px;
  background: ${({ theme }) => theme.whiteColor};
  padding: 0 5px;
  display: inline-block;
  vertical-align: middle;
  width: ${({ $fullWidthTitle }) => ($fullWidthTitle ? "100%" : "auto")};
`;

const FormGroup = styled.div`
  margin: 41px 0 27px;
  border: 2px solid ${({ theme }) => theme.greyColor20};
  box-sizing: border-box;
  border-radius: 8px;
  padding: 0 20px;
`;

interface GroupControlsProps {
  title: React.ReactNode;
  description?: string;
  name?: string;
  fullWidthTitle?: boolean;
}

const GroupControls: React.FC<GroupControlsProps> = ({
  title,
  description,
  children,
  name,
  fullWidthTitle = false,
}) => {
  return (
    <FormGroup data-testid={name}>
      <GroupTitle $fullWidthTitle={fullWidthTitle}>{title}</GroupTitle>
      {description && <Label message={<TextWithHTML text={description} />} />}
      {children}
    </FormGroup>
  );
};

export default GroupControls;
