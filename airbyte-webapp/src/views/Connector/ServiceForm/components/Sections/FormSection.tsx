import React, { useMemo } from "react";

import { FormBlock } from "core/form/types";

import { useServiceForm } from "../../serviceFormContext";
import { makeConnectionConfigurationPath, OrderComparator } from "../../utils";
import { ArraySection } from "./ArraySection";
import { AuthSection } from "./auth/AuthSection";
import { SectionContainer } from "./common";
import { ConditionSection } from "./ConditionSection";
import { PropertySection } from "./PropertySection";

interface FormNodeProps {
  sectionPath: string;
  formField: FormBlock;
  disabled?: boolean;
}

const FormNode: React.FC<FormNodeProps> = ({ sectionPath, formField, disabled }) => {
  if (formField._type === "formGroup") {
    return (
      <FormSection path={sectionPath} blocks={formField.properties} hasOauth={formField.hasOauth} disabled={disabled} />
    );
  } else if (formField._type === "formCondition") {
    return <ConditionSection path={sectionPath} formField={formField} disabled={disabled} />;
  } else if (formField._type === "objectArray") {
    return <ArraySection path={sectionPath} formField={formField} disabled={disabled} />;
  } else if (formField.const !== undefined) {
    return null;
  }
  return (
    <SectionContainer>
      <PropertySection property={formField} path={sectionPath} disabled={disabled} />
    </SectionContainer>
  );
};

interface FormSectionProps {
  blocks: FormBlock[] | FormBlock;
  path?: string;
  skipAppend?: boolean;
  hasOauth?: boolean;
  disabled?: boolean;
}

const FormSection: React.FC<FormSectionProps> = ({ blocks = [], path, skipAppend, hasOauth, disabled }) => {
  const sections = useMemo(() => {
    const flattenedBlocks = [blocks].flat();

    if (flattenedBlocks.some((b) => Number.isInteger(b.order))) {
      return flattenedBlocks.sort(OrderComparator);
    }

    return flattenedBlocks;
  }, [blocks]);

  const { selectedConnector, isAuthFlowSelected, authFieldsToHide } = useServiceForm();

  return (
    <>
      {hasOauth && <AuthSection key="authSection" />}
      {sections
        .filter(
          (formField) =>
            !formField.airbyte_hidden &&
            // TODO: check that it is a good idea to add authFieldsToHide
            (!isAuthFlowSelected || (isAuthFlowSelected && !authFieldsToHide.includes(formField.path)))
        )
        .map((formField) => {
          const sectionPath = path ? (skipAppend ? path : `${path}.${formField.fieldKey}`) : formField.fieldKey;

          const isAuthSection =
            isAuthFlowSelected &&
            selectedConnector?.advancedAuth?.predicateKey &&
            sectionPath === makeConnectionConfigurationPath(selectedConnector?.advancedAuth?.predicateKey);

          return (
            <React.Fragment key={sectionPath}>
              {isAuthSection && <AuthSection />}
              <FormNode formField={formField} sectionPath={sectionPath} disabled={disabled} />
            </React.Fragment>
          );
        })}
    </>
  );
};

export { FormSection };
