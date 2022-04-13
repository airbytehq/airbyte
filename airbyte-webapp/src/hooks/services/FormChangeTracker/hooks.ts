import { useCallback, useMemo } from "react";
import { createGlobalState } from "react-use";
import { useLocation } from "react-router-dom";
import { uniqueId } from "lodash";

import { FormChangeTrackerServiceApi } from "./types";

export const useChangedFormsById = createGlobalState<Record<string, boolean>>({});

export const useUniqueFormId = (formId?: string) => {
  const location = useLocation();
  return useMemo(
    () => formId ?? `${location.pathname.toLowerCase().replace(/\//gi, "_")}__${uniqueId("form_")}`,
    [formId, location.pathname]
  );
};

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
      if (!!changedFormsById?.[id] !== changed) {
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
