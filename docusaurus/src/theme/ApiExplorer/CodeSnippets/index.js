import { createStorageSlot } from "@docusaurus/theme-common";
import OriginalCodeSnippets from "@theme-original/ApiExplorer/CodeSnippets";

const codeSamplesStorage = createStorageSlot("docusaurus.tab.code-samples");

export default function CodeSnippets(props) {
  if (typeof window !== "undefined") {
    const language = codeSamplesStorage.get();
    if (language) {
      try {
        window.localStorage.setItem("docusaurus.tab.code-samples", language);
      } catch {
        return <OriginalCodeSnippets {...props} />;
      }
    }
  }

  return <OriginalCodeSnippets {...props} />;
}
