import { useState, useEffect } from "react";

import { RevealProps } from "config";

export const useReveal = () => {
  const [reveal, setReveal] = useState<RevealProps | null>(null);

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
