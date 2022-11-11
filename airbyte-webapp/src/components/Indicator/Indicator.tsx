import styled from "styled-components";

const Indicator = styled.div`
  height: 10px;
  width: 10px;
  border-radius: 50%;
  background: ${({ theme }) => theme.dangerColor};
`;

export default Indicator;
