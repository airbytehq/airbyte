import uniqueId from "lodash/uniqueId";
import { useCallback, useMemo, useRef } from "react";
import { createGlobalState } from "react-use";

import { FormChangeTrackerServiceApi } from "./types";

export const useChangedFormsById = createGlobalState<Record<string, boolean>>({});

export const useUniqueFormId = (formId?: string) => useMemo(() => formId ?? uniqueId("form_"), [formId]);

export const useFormChangeTrackerService = (): FormChangeTrackerServiceApi => {
  const [changedFormsById, setChangedFormsById] = useChangedFormsById();
  const changedFormsByIdRef = useRef(changedFormsById);
  changedFormsByIdRef.current = changedFormsById;

  const hasFormChanges = useMemo<boolean>(
    () => Object.values(changedFormsById ?? {}).some((changed) => !!changed),
    [changedFormsById]
  );

  const clearAllFormChanges = useCallback(() => {
    setChangedFormsById({});
  }, [setChangedFormsById]);

  const clearFormChange = useCallback(
    (id: string) => {
      setChangedFormsById({ ...changedFormsByIdRef.current, [id]: false });
    },
    [changedFormsByIdRef, setChangedFormsById]
  );

  const trackFormChange = useCallback(
    (id: string, changed: boolean) => {
      if (Boolean(changedFormsByIdRef.current?.[id]) !== changed) {
        setChangedFormsById({ ...changedFormsByIdRef.current, [id]: changed });
      }
    },
    [changedFormsByIdRef, setChangedFormsById]
  );

  return {
    hasFormChanges,
    trackFormChange,
    clearFormChange,
    clearAllFormChanges,
  };
};
