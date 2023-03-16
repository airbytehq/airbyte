import { Form as FormikForm } from "formik";
import styled from "styled-components";

export const Form = styled(FormikForm)`
  margin-top: 40px;
`;

export const FieldItem = styled.div<{
  bottom?: string;
}>`
  margin-bottom: ${({ bottom }) => (bottom ? bottom : 21)}px;
`;

export const RowFieldItem = styled(FieldItem)`
  display: flex;
  flex-direction: column;

  & > div {
    flex: 1 0 0;
    margin-right: 14px;
    margin-bottom: ${({ bottom }) => (bottom ? bottom : 21)}px;

    &:last-child {
      margin-right: 0;
      margin-bottom: 0;
    }
  }

  @media screen and (min-width: 769px) {
    flex-direction: row;
    & > div {
      margin-bottom: 0;
    }
  }
`;

export const BottomBlock = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  margin-top: 40px;
  font-size: 11px;
`;
