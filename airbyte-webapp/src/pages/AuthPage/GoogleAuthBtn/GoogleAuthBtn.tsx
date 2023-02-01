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
// import React from 'react';
// import { FormattedMessage } from "react-intl";
// import styled from "styled-components";

// import { LoadingButton } from "components";
// import { useGoogleLogin } from "@react-oauth/google";

// import { GoogleIcon } from "components/icons/GoogleIcon";

// const AuthBtn = styled(LoadingButton)`
//     width: 100%;
//     background-color: ${({theme}) => theme.white};
//     border: 1px solid #E0E3E7;
//     color: #6B6B6F;
//     border-radius: 6px;
// `;

// const BtnTextIconContainer = styled.div`
//     display: flex;
//     flex-direction: row;
//     align-items: center;
//     justify-content: center;
// `;

// const BtnText = styled.div`
//     font-style: normal;
//     font-weight: 500;
//     font-size: 13px;
//     color: #6B6B6F;
// `;

// export const GoogleAuthBtn: React.FC = () => {
//     const googleLogin = useGoogleLogin({
//         onSuccess: (codeResponse) => {
//             console.log(codeResponse);
//         },
//         onError: () => {
//             console.log("GOOGLE LOGIN FAILED");
//         }
//     });
//     return (
//         <AuthBtn onClick={() => googleLogin()} type="button">
//             <BtnTextIconContainer>
//                 <GoogleIcon />
//                 <BtnText>
//                     <FormattedMessage id="signup.google" />
//                 </BtnText>
//             </BtnTextIconContainer>
//         </AuthBtn>
//     );
// };
