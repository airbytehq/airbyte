import { JSONSchema7Type } from "json-schema";
import React from "react";
import { FormattedMessage } from "react-intl";

import { TextWithHTML } from "components/ui/TextWithHTML";

import styles from "./LabelInfo.module.scss";

interface LabelInfoProps {
  label: React.ReactNode;
  examples?: JSONSchema7Type;
  description?: string;
  options?: Array<{ title: string; description?: string }>;
}

const Description: React.FC<Pick<LabelInfoProps, "label" | "description">> = ({ label, description }) => {
  if (!description) {
    return null;
  }

  return (
    <div>
      {/* don't use <Text as=h4> here, because we want the default parent styling for this header */}
      <h3 className={styles.descriptionHeader}>{label}</h3>
      <TextWithHTML className={styles.description} text={description} />
    </div>
  );
};

const Options: React.FC<Pick<LabelInfoProps, "options">> = ({ options }) => {
  if (!options) {
    return null;
  }

  return (
    <div>
      <h4 className={styles.optionsHeader}>
        <FormattedMessage id="connector.optionsHeader" />
      </h4>
      <ul className={styles.options}>
        {options.map((option) => (
          <li key={option.title}>
            <strong>{option.title}</strong>
            {option.description && (
              <>
                {" "}
                - <TextWithHTML className={styles.description} text={option.description} />
              </>
            )}
          </li>
        ))}
      </ul>
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
      <h4 className={styles.exampleHeader}>
        <FormattedMessage id="connector.exampleValues" values={{ count: examplesArray.length }} />
      </h4>
      <div className={styles.exampleContainer}>
        {examplesArray.map((example) => (
          <span className={styles.exampleItem}>{String(example)}</span>
        ))}
      </div>
    </div>
  );
};

export const LabelInfo: React.FC<LabelInfoProps> = ({ label, examples, description, options }) => {
  return (
    <div className={styles.container}>
      <Description label={label} description={description} />
      <Options options={options} />
      <Examples examples={examples} />
    </div>
  );
};
