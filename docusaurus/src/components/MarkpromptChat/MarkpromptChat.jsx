import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import "@markprompt/css";
import { Markprompt } from "@markprompt/react";
import React from "react";
import ChatTrigger from "./ChatTrigger";
import "./ChatTrigger.module.css";

export default function MarkpromptChat() {
  const {
    siteConfig: {
      customFields: { markpromptProjectKey },
    },
  } = useDocusaurusContext();
  return (
    <Markprompt
      projectKey={markpromptProjectKey}
      defaultView="chat"
      customElement={true}
      display="sheet"
      chat={{
        assistantId: "d1399022-d7e2-4404-bd16-8b3ad2b5465b",
        enabled: true,
        defaultView: {
          message:
            "Hi! I'm Octavia. How can I help? **I'm an AI, but I'm still learning and might make mistakes**. ",
          prompts: [
            "What's Airbyte?",
            "Can I try Airbyte quickly?",
            "How do I use Terraform with Airbyte?",
            "Is there an enterprise version?",
          ],
        },
        display: "sheet",
        avatars: {
          assistant: "/img/octavia-talking.png",
        },
      }}
    >
      <ChatTrigger />
    </Markprompt>
  );
}
