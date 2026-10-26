// Idempotent base init for source-mongodb-v2 e2e tests (non-CDC).
// mongosh starts in test_db (BACKEND_DB); this fixture (re)creates a small
// sample collection with three documents.

db.sample.drop();

db.sample.insertMany([
  { _id: 1, label: "alpha" },
  { _id: 2, label: "beta" },
  { _id: 3, label: "gamma" },
]);
