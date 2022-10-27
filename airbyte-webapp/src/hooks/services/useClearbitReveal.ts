import { useState, useEffect } from "react";

import { ClearbitRevealProps } from "config";

export const useClearbitReveal = () => {
  const [reveal, setReveal] = useState<ClearbitRevealProps | null>(null);

  useEffect(() => {
    function onReveal() {
      setReveal(window.reveal);
    }

    window.addEventListener("reveal", onReveal);
    onReveal();

    return () => window.removeEventListener("reveal", onReveal);
  }, []);

  return reveal;
};
