import { createStorageSlot } from "@docusaurus/theme-common";
import OriginalCodeSnippets from "@theme-original/ApiExplorer/CodeSnippets";

const codeSamplesStorage = createStorageSlot("docusaurus.tab.code-samples");

function syncCodeSamplesStorage() {
  try {
    const language = codeSamplesStorage.get();
    if (language) {
      window.localStorage.setItem("docusaurus.tab.code-samples", language);
    }
  } catch {
    // Storage is unavailable.
  }
}

export default function CodeSnippets(props) {
  if (typeof window !== "undefined") {
    syncCodeSamplesStorage();
  }
  return <OriginalCodeSnippets {...props} />;
}
