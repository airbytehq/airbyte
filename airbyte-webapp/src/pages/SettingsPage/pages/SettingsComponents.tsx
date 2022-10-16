import styled from "styled-components";

import { Card } from "components/ui/Card";

export const SettingsCard = styled(Card)`
  width: 100%;

  &:not(:first-child) {
    margin-top: 10px;
  }
`;

export const Content = styled.div`
  padding: 27px 26px 15px;
`;
