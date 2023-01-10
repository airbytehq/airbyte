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

  const { trackFormChange, clearFormChange } = useFormChangeTrackerService();

  useEffect(() => {
    if (changed !== prevChanged) {
      trackFormChange(id, changed);
    }
  }, [id, changed, trackFormChange, prevChanged]);

  // when the form id changes or the change tracker gets unmounted completely,
  // clear out the old form as it's not relevant anymore
  useEffect(() => {
    return () => {
      clearFormChange(id);
    };
  }, [clearFormChange, id]);

  return null;
};
