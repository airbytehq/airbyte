import React, { useState } from "react";
import styled from "styled-components";

import SubmitSuccess from "./components/SubmitSuccess";
import SupportForm from "./components/SupportForm";

const SupportContainer = styled.div`
  width: 80%;
  // max-width: 686px;
  padding: 30px 70px;
  margin: 0 auto;
`;

const SupportPage: React.FC = () => {
  const [isSubmit, setSubmitState] = useState<boolean>(false);

  const onSubmit = () => {
    setSubmitState(true);
    setTimeout(() => {
      setSubmitState(false);
    }, 5000);
  };

  return (
    <SupportContainer>
      {!isSubmit && <SupportForm onSubmit={onSubmit} />}
      {isSubmit && <SubmitSuccess />}
    </SupportContainer>
  );
};

export default SupportPage;
