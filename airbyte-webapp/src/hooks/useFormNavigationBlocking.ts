import { useCallback, useMemo } from "react";
import { createGlobalState } from "react-use";

import { usePrompt } from "./router/usePrompt";

export const useBlockingFormsById = createGlobalState<Record<string, boolean>>({});

const useFormNavigationBlockingPrompt = () => {
  const [blockingFormsById, setBlockingFormsById] = useBlockingFormsById();

  const isFormBlocking = useMemo(
    () => Object.values(blockingFormsById ?? {}).reduce((acc, value) => acc || value, false),
    [blockingFormsById]
  );

  const onConfirm = useCallback(() => {
    setBlockingFormsById({});
  }, [setBlockingFormsById]);

  usePrompt("Navigate to another page? Changes you made will not be saved.", isFormBlocking, onConfirm);
};

export default useFormNavigationBlockingPrompt;
