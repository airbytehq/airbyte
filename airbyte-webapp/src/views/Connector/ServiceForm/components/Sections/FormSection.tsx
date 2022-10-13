import React, { useMemo } from "react";

import { FormBlock } from "core/form/types";

import { useAuthentication } from "../../useAuthentication";
import { OrderComparator } from "../../utils";
import { ArraySection } from "./ArraySection";
import { AuthSection } from "./auth/AuthSection";
import { ConditionSection } from "./ConditionSection";
import { PropertySection } from "./PropertySection";
import { SectionContainer } from "./SectionContainer";

interface FormNodeProps {
  sectionPath: string;
  formField: FormBlock;
  disabled?: boolean;
}

const FormNode: React.FC<FormNodeProps> = ({ sectionPath, formField, disabled }) => {
  if (formField._type === "formGroup") {
    return <FormSection path={sectionPath} blocks={formField.properties} disabled={disabled} />;
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
  disabled?: boolean;
}

export const FormSection: React.FC<FormSectionProps> = ({ blocks = [], path, skipAppend, disabled }) => {
  const sections = useMemo(() => {
    const flattenedBlocks = [blocks].flat();

    if (flattenedBlocks.some((b) => Number.isInteger(b.order))) {
      return flattenedBlocks.sort(OrderComparator);
    }

    return flattenedBlocks;
  }, [blocks]);

  const { isFieldImplicitAuthField, isAuthFlowSelected, oAuthButtonPath } = useAuthentication();

  return (
    <>
      {sections
        .filter(
          (formField) =>
            !formField.airbyte_hidden &&
            (!isAuthFlowSelected || (isAuthFlowSelected && !isFieldImplicitAuthField(formField.path)))
        )
        .map((formField) => {
          const sectionPath = path ? (skipAppend ? path : `${path}.${formField.fieldKey}`) : formField.fieldKey;

          return (
            <React.Fragment key={sectionPath}>
              <div style={{ background: "hotpink" }}>
                {sectionPath} (_type: {formField._type})
              </div>
              {isAuthFlowSelected && oAuthButtonPath === sectionPath && formField._type !== "formCondition" && (
                <AuthSection />
              )}
              <FormNode formField={formField} sectionPath={sectionPath} disabled={disabled} />
            </React.Fragment>
          );
        })}
    </>
  );
};
