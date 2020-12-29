import styled from "styled-components";

const CenteredDetails = styled.div`
  text-align: center;
  padding-top: 9px;
  font-size: 12px;
  line-height: 28px;
  color: ${({ theme }) => theme.greyColor40};
  position: relative;
`;

export default CenteredDetails;
