SELECT * FROM menu
SELECT * FROM users

DROP TABLE IF EXISTS menu;

CREATE TABLE menu
(
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price TEXT NOT NULL,
    alcoholic TEXT NOT NULL,
    type TEXT NOT NULL,
    picture TEXT DEFAULT 'Default.jpeg'
);

INSERT INTO menu (name, price, alcoholic, type, picture)
VALUES 
    ('Beer', '6.70', 'Alcoholic', 'Drink', 'Beer.jpg'),
    ('Water', '2.00', 'Non-Alcoholic', 'Drink', 'Water.jpg'),
    ('Cider', '7.20', 'Alcoholic', 'Drink', 'Cider.jpg'),
    ('Coffee', '5.00', 'Non-Alcoholic', 'Drink', 'Coffee.jpg'),
    ('Spirit', '8.40', 'Alcoholic', 'Drink', 'Spirit.jpg'),
    ('Steak', '27.50', 'Non-Alcoholic', 'Food', 'Steak.jpg'),
    ('Salad', '14.00', 'Non-Alcoholic', 'Food', 'Salad.jpg'),
    ('Chips', '5.00', 'Non-Alcoholic', 'Food', 'Chips.jpg'),
    ('Burger', '16.70', 'Non-Alcoholic', 'Food', 'Burger.jpg'),
    ('Salmon', '23.00', 'Non-Alcoholic', 'Food', 'Salmon.jpg');

DROP TABLE IF EXISTS users;

CREATE TABLE users
(
    user_id TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    admin NUMBER DEFAULT 0
);

INSERT INTO users(user_id, password, admin) 
VALUES
    ('admin', 'scrypt:32768:8:1$SoLAvYZhICjrrhDO$5b55d674af70cc740cb7bb96e48b7bc602391ea7dd961bf99fd8e1b0c075bd6fbbac7669f8da88620691068a40d434a5c757434e106f09d704fb83dc23201474', '1');
