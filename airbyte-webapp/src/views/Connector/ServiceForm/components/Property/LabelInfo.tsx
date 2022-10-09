import { JSONSchema7Type } from "json-schema";
import React from "react";

import { TextWithHTML } from "components/ui/TextWithHTML";

import styles from "./LabelInfo.module.scss";

interface LabelInfoProps {
  label: React.ReactNode;
  examples?: JSONSchema7Type;
  description?: string;
}

const Description: React.FC<Pick<LabelInfoProps, "label" | "description">> = ({ label, description }) => {
  if (!description) {
    return null;
  }

  return (
    <div>
      {/* don't use <Text as=h4> here, because we want the default parent styling for this header */}
      <h4 className={styles.descriptionHeader}>{label}</h4>
      <TextWithHTML className={styles.description} text={description} />
    </div>
  );
};

const Examples: React.FC<Pick<LabelInfoProps, "examples">> = ({ examples }) => {
  if (!examples) {
    return null;
  }

  const examplesArray = Array.isArray(examples) ? examples : [examples];

  return (
    <div>
      {/* don't use <Text as=h4> here, because we want the default parent styling for this header */}
      <h4 className={styles.exampleHeader}>{`Example value${examplesArray.length > 1 ? "s" : ""}`}</h4>
      <div className={styles.exampleContainer}>
        {examplesArray.map((example) => (
          <span className={styles.exampleItem}>{example}</span>
        ))}
      </div>
    </div>
  );
};

export const LabelInfo: React.FC<LabelInfoProps> = ({ label, examples, description }) => {
  return (
    <div className={styles.container}>
      <Description label={label} description={description} />
      <Examples examples={examples} />
    </div>
  );
};
