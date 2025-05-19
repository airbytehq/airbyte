import "@markprompt/css";
import { Markprompt } from "@markprompt/react";
import React from "react";
import ChatTrigger from "./ChatTrigger";
import "./ChatTrigger.module.css";

export default function MarkpromptChat() {
  return (
    <Markprompt
      projectKey="pk_c87ydSnE4o1tX9txQReh3vDvVnKDnbje" // public key, safe to commit
      defaultView="chat"
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
