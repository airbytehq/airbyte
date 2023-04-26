import styled from "styled-components";

import { LoadingButton, Link } from "components";

import { Form } from "../../components/FormComponents";

export const Title = styled.div`
  color: #27272a;
  padding-top: 35px;
  font-style: normal;
  font-weight: 600;
  font-size: 24px;
  line-height: 28px;
  margin-bottom: 30px;
`;

export const SubTitle = styled.div`
  font-weight: 400;
  font-size: 16px;
  line-height: 20px;
  text-align: center;
  color: #6b6b6f;
  margin-bottom: 80px;
`;

export const SubmitButton = styled(LoadingButton)`
  width: 100% !important;
  font-weight: 600 !important;
  font-size: 16px !important;
  line-height: 19px !important;
  height: 44px !important;
  margin-top: 50px;
`;

export const EmailText = styled.div`
  font-weight: 500;
  font-size: 20px;
  line-height: 24px;
  text-align: center;
  color: #27272a;
  margin: 30px 0 60px 0;
`;

export const FormContainer = styled(Form)`
  width: 100%;
`;

export const LinkContainer = styled.div`
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
`;

export const Lnk = styled(Link)`
  font-weight: 500;
  font-size: 15px;
  text-align: center;
`;
