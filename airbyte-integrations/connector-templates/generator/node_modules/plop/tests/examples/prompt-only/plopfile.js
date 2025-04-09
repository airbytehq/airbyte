export default function (plop) {
  plop.setGenerator("test", {
    description: "this is a test",
    prompts: [
      {
        type: "input",
        name: "name",
        message: "What is your name?",
      },
      {
        type: "checkbox",
        name: "toppings",
        message: "What pizza toppings do you like?",
        choices: [
          { name: "Cheese", value: "cheese", checked: true },
          { name: "Pepperoni", value: "pepperoni" },
          { name: "Pineapple", value: "pineapple" },
          { name: "Mushroom", value: "mushroom" },
          { name: "Bacon", value: "bacon", checked: true },
        ],
      },
    ],
  });
}
