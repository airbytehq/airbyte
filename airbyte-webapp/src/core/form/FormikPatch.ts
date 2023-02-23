import { flatten } from "flat";
import { useFormikContext } from "formik";
import { useEffect } from "react";

export const FormikPatch: React.FC = () => {
  const { setFieldTouched, isSubmitting, isValidating, errors } = useFormikContext();

  /* Fixes issue https://github.com/airbytehq/airbyte/issues/1978
     Problem described here https://github.com/formium/formik/issues/445
     The problem is next:

     When we touch the field, it would be set as touched field correctly.
     If validation fails on submit - Formik detects touched object mapping based
     either on initialValues passed to Formik or on current value set.
     So in case of creation, if we touch an input, don't change value and
     press submit - our touched map will be cleared.

     This hack just touches all fields on submit.
   */
  useEffect(() => {
    if (isSubmitting && !isValidating) {
      for (const path of Object.keys(flatten(errors))) {
        setFieldTouched(path, true, false);
      }
    }
  }, [errors, isSubmitting, isValidating, setFieldTouched]);

  return null;
};
