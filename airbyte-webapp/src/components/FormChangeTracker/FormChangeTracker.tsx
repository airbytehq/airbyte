import { useLayoutEffect, useMemo } from "react";
import { uniqueId } from "lodash";
import { useLocation } from "react-router-dom";
import { usePrevious } from "react-use";

import { useFormChangeTrackerService } from "hooks/services/FormChangeTracker";

interface Props {
  changed: boolean;
}

const FormChangeTracker: React.FC<Props> = ({ changed }) => {
  const location = useLocation();
  const id = useMemo(() => `${location.pathname}__${uniqueId("form_")}`, [location.pathname]);
  const prevChanged = usePrevious(changed);

  const { trackFormChange } = useFormChangeTrackerService();

  useLayoutEffect(() => {
    if (changed !== prevChanged) {
      trackFormChange(id, changed);
    }
  }, [id, changed, trackFormChange, prevChanged]);

  return null;
};

export default FormChangeTracker;
