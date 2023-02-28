import React from "react";
import { FormattedMessage } from "react-intl";

import { BigButton, ButtonRows } from "components/base/Button/BigButton";

interface Iprops {
  isLoading: boolean;
  onBack: () => void;
  onFinish: () => void;
}
const FooterButtons: React.FC<Iprops> = ({ isLoading, onBack, onFinish }) => {
  return (
    <ButtonRows bottom="40">
      <BigButton secondary type="button" onClick={onBack} disabled={isLoading}>
        <FormattedMessage id="form.button.back" />
      </BigButton>
      <BigButton onClick={onFinish} disabled={isLoading}>
        <FormattedMessage id="form.button.finish" />
      </BigButton>
    </ButtonRows>
  );
};

export default FooterButtons;
