import styled from "styled-components";

interface FormPageContentProps {
  big?: boolean;
}

const FormPageContent = styled.div<FormPageContentProps>`
  ${({ big }) => (big ? "" : "width: 80%; max-width: 813px;")}
  margin: 13px auto 0;
`;

export default FormPageContent;
