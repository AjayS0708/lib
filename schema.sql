-- Drop existing tables if they exist
DROP TABLE IF EXISTS titleauthor;
DROP TABLE IF EXISTS titles;
DROP TABLE IF EXISTS authors;

-- Authors table with extended fields
CREATE TABLE authors (
    au_id VARCHAR(11) PRIMARY KEY,
    au_name VARCHAR(100) NOT NULL,
    au_fname VARCHAR(50),
    phone VARCHAR(20),
    address VARCHAR(100),
    city VARCHAR(50),
    state VARCHAR(50),
    zip VARCHAR(10),
    contract BOOLEAN DEFAULT FALSE
);

-- Titles table with extended fields
CREATE TABLE titles (
    title_id VARCHAR(6) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    type VARCHAR(50),
    pub_id VARCHAR(4),
    price DECIMAL(10, 2),
    advance DECIMAL(10, 2),
    royalty INT,
    ytd_sales INT,
    notes TEXT,
    pubdate DATE
);

-- TitleAuthor junction table with royalty percentage
CREATE TABLE titleauthor (
    au_id VARCHAR(11),
    title_id VARCHAR(6),
    au_ord INT,
    royaltyper INT,
    PRIMARY KEY (au_id, title_id),
    FOREIGN KEY (au_id) REFERENCES authors(au_id) ON DELETE CASCADE,
    FOREIGN KEY (title_id) REFERENCES titles(title_id) ON DELETE CASCADE
);

-- Sample data for authors (au_id, au_fname, au_name)
INSERT INTO authors (au_id, au_fname, au_name, phone, address, city, state, zip, contract) VALUES
('1', 'Vimal', 'Johnson', '+91 98765 43210', '10932 Bigge Rd.', 'Mumbai', 'Maharashtra', '400001', TRUE),
('2', 'Girish', 'Marjorie', '+91 91234 56789', '309 63rd St. #411', 'Bengaluru', 'Karnataka', '560001', TRUE),
('3', 'Chinmau', 'Cheryl', '+91 99876 54321', '589 Darwin Ln.', 'Chennai', 'Tamil Nadu', '600001', TRUE),
('4', 'Owen', 'Michael', '+91 90123 45678', '22 Cleveland Av. #14', 'Pune', 'Maharashtra', '411001', TRUE),
('5', 'Sri', 'Dean', '+91 92211 33445', '5420 College Av.', 'Kolkata', 'West Bengal', '700001', TRUE);

-- Sample data for titles
INSERT INTO titles (title_id, title, type, pub_id, price, advance, royalty, ytd_sales, notes, pubdate) VALUES
('BU1', 'The Busy Executive''s Database Guide', 'business', '1389', 19.99, 5000.00, 10, 4095, 'An overview of available database systems', '2023-06-12'),
('BU2', 'Cooking with Computers: Surreptitious Balance Sheets', 'business', '1389', 11.95, 5000.00, 10, 3876, 'Helpful hints on how to use your computer', '2023-06-09'),
('BU3', 'You Can Combat Computer Stress!', 'business', '0736', 2.99, 10125.00, 24, 18722, 'Latest medical and psychological techniques', '2023-06-30'),
('BU4', 'Straight Talk About Computers', 'business', '1389', 19.99, 5000.00, 10, 4095, 'Annotated analysis of what computers can do', '2023-06-22'),
('BU5', 'Silicon Valley Gastronomic Treats', 'mod_cook', '0877', 19.99, 0.00, 12, 2032, 'Favorite recipes from Silicon Valley', '2023-06-09');

-- Sample data for titleauthor
INSERT INTO titleauthor (au_id, title_id, au_ord, royaltyper) VALUES
('1', 'BU1', 1, 60),
('2', 'BU1', 2, 40),
('3', 'BU2', 1, 100),
('4', 'BU2', 2, 0),
('5', 'BU4', 1, 100);

-- Simple select for manual verification
SELECT * FROM titles;
