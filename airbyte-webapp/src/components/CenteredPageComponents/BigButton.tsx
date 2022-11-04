import styled from "styled-components";

import { Button } from "components";
const BigButton = styled(Button)<{ shadow?: boolean }>`
  background-color: #4f46e5;
  border-radius: 25px;
  font-size: 16px;
  line-height: 19px;
  padding: 15px 30px;
  font-weight: 500;
  //box-shadow: ${({ shadow }) => (shadow ? "0 8px 5px -5px rgba(0, 0, 0, 0.2)" : "none")};
`;

export default BigButton;
