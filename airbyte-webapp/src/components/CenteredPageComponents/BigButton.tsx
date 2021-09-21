import styled from "styled-components";

import { Button } from "components";
const BigButton = styled(Button)<{ shadow?: boolean }>`
  font-size: 16px;
  line-height: 19px;
  padding: 10px 27px;
  font-weight: 500;
  box-shadow: ${({ shadow }) =>
    shadow ? "0 8px 5px -5px rgba(0, 0, 0, 0.2)" : "none"};
`;

export default BigButton;
