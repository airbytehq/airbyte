CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    city TEXT,
    signup_date DATE
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    price NUMERIC(10, 2),
    in_stock BOOLEAN DEFAULT TRUE
);

CREATE TABLE order_items (
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price NUMERIC(10, 2),
    PRIMARY KEY (order_id, product_id)
);

INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
  (1, 1, 1, 149.99),
  (1, 3, 2, 79.50),
  (2, 2, 1, 429.00),
  (2, 5, 3, 54.00),
  (3, 6, 1, 299.00),
  (4, 1, 1, 149.99),
  (4, 4, 2, 39.90),
  (5, 2, 2, 429.00);

INSERT INTO users (name, email, city, signup_date) VALUES
  ('Ada Lovelace', 'ada@example.com', 'London', '2024-01-15'),
  ('Grace Hopper', 'grace@example.com', 'New York', '2024-02-20'),
  ('Alan Turing', 'alan@example.com', 'Cambridge', '2024-03-10'),
  ('Margaret Hamilton', 'margaret@example.com', 'Boston', '2024-04-05'),
  ('Linus Torvalds', 'linus@example.com', 'Helsinki', '2024-05-12');

INSERT INTO products (title, description, price, in_stock) VALUES
  ('Mechanical Keyboard', 'Tactile switches, aluminium frame', 149.99, TRUE),
  ('4K Monitor', '27 inch IPS panel with USB-C', 429.00, TRUE),
  ('Ergonomic Mouse', 'Vertical grip, wireless', 79.50, TRUE),
  ('Laptop Stand', 'Foldable aluminium stand', 39.90, FALSE),
  ('USB-C Hub', '7-in-1 hub with HDMI and ethernet', 54.00, TRUE),
  ('Noise-Cancelling Headphones', 'Over-ear, 30h battery', 299.00, TRUE);
