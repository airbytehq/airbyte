import React, { useMemo } from "react";

import { FormBlock } from "core/form/types";

import { ArraySection } from "./ArraySection";
import { AuthSection } from "./auth/AuthSection";
import { ConditionSection } from "./ConditionSection";
import { PropertySection } from "./PropertySection";
import { SectionContainer } from "./SectionContainer";
import { useAuthentication } from "../../useAuthentication";
import { OrderComparator } from "../../utils";

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
  const { isHiddenAuthField, shouldShowAuthButton } = useAuthentication();

  const sections = useMemo(() => {
    const flattenedBlocks = [blocks].flat();

    if (flattenedBlocks.some((b) => Number.isInteger(b.order))) {
      return flattenedBlocks.sort(OrderComparator);
    }

    return flattenedBlocks;
  }, [blocks]);

  return (
    <>
      {sections
        .filter((formField) => !formField.airbyte_hidden && !isHiddenAuthField(formField.path))
        .map((formField) => {
          const sectionPath = path ? (skipAppend ? path : `${path}.${formField.fieldKey}`) : formField.fieldKey;

          return (
            <React.Fragment key={sectionPath}>
              {/*
                If the auth button should be rendered here, do so. In addition to the check useAuthentication does
                we also need to check if the formField type is not a `formCondition`. We render a lot of OAuth buttons
                in conditional fields in which case the path they should be rendered is the path of the conditional itself.
                For conditional fields we're rendering this component twice, once "outside" of the conditional, which causes
                the actual conditional frame to be rendered and once inside the conditional to render the actual content.
                Since we want to only render the auth button inside the conditional and not above it, we filter out the cases
                where the formField._type is formCondition, which will be the "outside rendering".
               */}
              {shouldShowAuthButton(sectionPath) && formField._type !== "formCondition" && <AuthSection />}
              <FormNode formField={formField} sectionPath={sectionPath} disabled={disabled} />
            </React.Fragment>
          );
        })}
    </>
  );
};
