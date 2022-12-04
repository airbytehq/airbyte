import { useEffect } from "react";
import { usePrevious } from "react-use";

import { useFormChangeTrackerService, useUniqueFormId } from "hooks/services/FormChangeTracker";

interface Props {
  changed: boolean;
  formId?: string;
}

export const FormChangeTracker: React.FC<Props> = ({ changed, formId }) => {
  const id = useUniqueFormId(formId);
  const prevChanged = usePrevious(changed);

  const { trackFormChange } = useFormChangeTrackerService();

  useEffect(() => {
    if (changed !== prevChanged) {
      trackFormChange(id, changed);
    }
  }, [id, changed, trackFormChange, prevChanged]);

  return null;
};
