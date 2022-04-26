import { uniqueId } from "lodash";
import { useCallback, useMemo } from "react";
import { createGlobalState } from "react-use";

import { FormChangeTrackerServiceApi } from "./types";

export const useChangedFormsById = createGlobalState<Record<string, boolean>>({});

export const useUniqueFormId = (formId?: string) => useMemo(() => formId ?? uniqueId("form_"), [formId]);

export const useFormChangeTrackerService = (): FormChangeTrackerServiceApi => {
  const [changedFormsById, setChangedFormsById] = useChangedFormsById();

  const clearAllFormChanges = useCallback(() => {
    setChangedFormsById({});
  }, [setChangedFormsById]);

  const clearFormChange = useCallback(
    (id: string) => {
      setChangedFormsById({ ...changedFormsById, [id]: false });
    },
    [changedFormsById, setChangedFormsById]
  );

  const trackFormChange = useCallback(
    (id: string, changed: boolean) => {
      if (Boolean(changedFormsById?.[id]) !== changed) {
        setChangedFormsById({ ...changedFormsById, [id]: changed });
      }
    },
    [changedFormsById, setChangedFormsById]
  );

  return {
    trackFormChange,
    clearFormChange,
    clearAllFormChanges,
  };
};
