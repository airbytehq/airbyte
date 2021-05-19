import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { LabeledRadioButton, Link } from "components";
import { Normalisation } from "../types";

const Normalization = styled.div`
  margin: 16px 0;
`;

type NormalizationBlockProps = {
  value: string;
  onClick: (value: string) => void;
};

const NormalizationBlock: React.FC<NormalizationBlockProps> = ({
  value,
  onClick,
}) => {
  return (
    <Normalization>
      <LabeledRadioButton
        label={<FormattedMessage id="form.rawData" />}
        checked={value === Normalisation.RAW}
        onClick={() => onClick(Normalisation.RAW)}
        name="rawData"
      />
      <LabeledRadioButton
        checked={value === Normalisation.BASIC}
        onClick={() => onClick(Normalisation.BASIC)}
        name="basicNormalization"
        message={
          <FormattedMessage
            id="form.basicNormalization.message"
            values={{
              lnk: (...lnk: React.ReactNode[]) => (
                // TODO: add link href
                <Link target="_blank" href={""} as="a">
                  {lnk}
                </Link>
              ),
            }}
          />
        }
        label={<FormattedMessage id="form.basicNormalization" />}
      />
    </Normalization>
  );
};

export default NormalizationBlock;
