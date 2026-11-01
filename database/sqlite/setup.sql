-- SQL Made Simple | SimpleStore v1.0 | SQLite
-- Run this script in a new SQLite database.
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS OrderItems;
DROP TABLE IF EXISTS Orders;
DROP TABLE IF EXISTS Products;
DROP TABLE IF EXISTS Customers;

CREATE TABLE Customers (
  CustomerID INTEGER PRIMARY KEY,
  CustomerName TEXT NOT NULL,
  City TEXT NOT NULL
);

CREATE TABLE Products (
  ProductID INTEGER PRIMARY KEY,
  ProductName TEXT NOT NULL,
  Category TEXT NOT NULL,
  UnitPrice NUMERIC NOT NULL CHECK (UnitPrice >= 0)
);

CREATE TABLE Orders (
  OrderID INTEGER PRIMARY KEY,
  CustomerID INTEGER NOT NULL REFERENCES Customers(CustomerID),
  OrderDate TEXT NOT NULL
);

CREATE TABLE OrderItems (
  OrderID INTEGER NOT NULL REFERENCES Orders(OrderID),
  ProductID INTEGER NOT NULL REFERENCES Products(ProductID),
  Quantity INTEGER NOT NULL CHECK (Quantity > 0),
  UnitPrice NUMERIC NOT NULL CHECK (UnitPrice >= 0),
  PRIMARY KEY (OrderID, ProductID)
);

INSERT INTO Customers VALUES
(1, 'Maya Chen', 'London'),
(2, 'Daniel Reed', 'Bristol'),
(3, 'Sofia Patel', 'London'),
(4, 'Leo Martin', 'Manchester'),
(5, 'Amira Hassan', 'Leeds');

INSERT INTO Products VALUES
(1, 'Notebook', 'Stationery', 4.50),
(2, 'Pen Set', 'Stationery', 7.00),
(3, 'Water Bottle', 'Accessories', 15.00),
(4, 'Desk Lamp', 'Home Office', 28.00),
(5, 'USB Cable', 'Electronics', 9.50),
(6, 'Backpack', 'Accessories', 42.00);

INSERT INTO Orders VALUES
(101, 1, '2026-01-05'),
(102, 2, '2026-01-06'),
(103, 1, '2026-01-11'),
(104, 3, '2026-01-13'),
(105, 4, '2026-01-16'),
(106, 2, '2026-02-02'),
(107, 3, '2026-02-10'),
(108, 1, '2026-02-14');

-- UnitPrice in OrderItems records the price at the time of sale.
INSERT INTO OrderItems VALUES
(101, 1, 2, 4.50), (101, 2, 1, 7.00),
(102, 3, 1, 15.00), (102, 5, 2, 9.50),
(103, 4, 1, 28.00),
(104, 1, 3, 4.50), (104, 6, 1, 42.00),
(105, 2, 2, 7.00),
(106, 5, 1, 9.50), (106, 1, 1, 4.50),
(107, 3, 2, 15.00),
(108, 6, 1, 42.00), (108, 5, 1, 9.50);
