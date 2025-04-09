export default function (plop) {
  plop.setGenerator("addAndNameFile", {
    description: "Name that file",
    prompts: [
      {
        type: "input",
        name: "fileName",
        message: "What should the file name be?",
      },
    ],
    actions: [
      {
        type: "add",
        path: "./output/{{fileName}}.txt",
        templateFile: "./templates/to-add.txt",
      },
    ],
  });

  plop.setGenerator("addAndChangeFile", {
    description: "Name that file",
    prompts: [
      {
        type: "input",
        name: "name",
        message: "What's your name?",
      },
    ],
    actions: [
      {
        type: "add",
        path: "./output/new-output.txt",
        templateFile: "./templates/to-add-change.txt",
      },
    ],
  });
}
