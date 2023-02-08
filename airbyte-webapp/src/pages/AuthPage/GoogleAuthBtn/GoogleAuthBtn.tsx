import { GoogleLogin } from "@react-oauth/google";
import React from "react";
import styled from "styled-components";

import { useUser } from "core/AuthContext";
import { useAuthenticationService } from "services/auth/AuthSpecificationService";

interface IProps {
  buttonText: "signup_with" | "signin_with" | "signin" | "continue_with";
}

const GoogleAuthButtonContainer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
`;

export const GoogleAuthBtn: React.FC<IProps> = ({ buttonText }) => {
  const auth = useAuthenticationService();
  const { setUser } = useUser();
  return (
    <GoogleAuthButtonContainer>
      <GoogleLogin
        text={buttonText}
        onSuccess={(credentialsResponse) => {
          auth
            .googleAuth(credentialsResponse.credential as string)
            .then((res) => {
              setUser?.(res);
            })
            .catch((err) => {
              console.log(err);
            });
        }}
        onError={() => {
          console.log("GOOGLE AUTHENTICATION FAILED");
        }}
      />
    </GoogleAuthButtonContainer>
  );
};
