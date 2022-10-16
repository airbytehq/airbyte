const stripe = require("stripe")("sk_test_4eC39HqLyjWDarjtT1zdp7dc");

async function test() {
  const charges = await stripe.charges.list({
    limit: 3,
  });

  console.log(charges);
}

test();
