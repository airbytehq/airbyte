export default function (plop) {
  plop.setGenerator("test", {
    description: "this is a test",
    prompts: [
      {
        type: "input",
        name: "name",
        message: "What is your name?",
      },
    ],
    actions: [
      () => {
        throw new Error("Action failed");
      },
    ],
  });
}
