import styled from "styled-components";

export const FlexRow = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  align-items: flex-start;
  gap: 10px;
`;

export const LeftFieldCol = styled.div`
  flex: 1;
  max-width: 640px;
  padding-right: 30px;
`;

export const RightFieldCol = styled.div`
  flex: 1;
  max-width: 300px;
`;

export const StyledSection = styled.div`
  padding: 20px 20px;
  display: flex;
  flex-direction: column;
  gap: 15px;

  &:not(:last-child) {
    box-shadow: 0 1px 0 rgba(139, 139, 160, 0.25);
  }
`;

export type ConnectionFormMode = "create" | "edit" | "readonly";
