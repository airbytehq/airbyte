import { useState, useRef, useCallback, useEffect } from "react";

function useStateCallback<T>(initialState: T): [T, (state: T, cb?: (state: T) => void) => void] {
  const [state, setState] = useState(initialState);
  const cbRef = useRef<((state: T) => void) | undefined>(undefined);

  const setStateCallback = useCallback((state: T, cb?: (state: T) => void) => {
    cbRef.current = cb;
    setState(state);
  }, []);

  useEffect(() => {
    if (cbRef.current) {
      cbRef.current(state);
      cbRef.current = undefined;
    }
  }, [state]);

  return [state, setStateCallback];
}

export default useStateCallback;
