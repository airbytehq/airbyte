import styled from "styled-components";
import { ContentCard } from "components/ContentCard";

export const SettingsCard = styled(ContentCard)`
  width: 100%;

  &:not(:first-child) {
    margin-top: 10px;
  }
`;

export const Content = styled.div`
  padding: 27px 26px 15px;
`;
