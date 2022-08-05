CREATE DATABASE VENDING;
USE VENDING;
CREATE TABLE TICKETS (
    ID CHAR(2) NOT NULL,
    ProductName VARCHAR(30),
    Price FLOAT(6,2),
    Stock INT,
    PRIMARY KEY (ID)
);

INSERT INTO TICKETS(ID, ProductName, Price, Stock)
VALUES ('A0','London to Glasgow', 108.5, 100); 

INSERT INTO TICKETS(ID, ProductName, Price, Stock)
VALUES ('A1','London to Leeds', 29, 55);

INSERT INTO TICKETS(ID, ProductName, Price, Stock)
VALUES ('A2','London to York', 28, 120);

INSERT INTO TICKETS(ID, ProductName, Price, Stock)
VALUES ('A3','London to Bristol', 35, 100);

INSERT INTO TICKETS(ID, ProductName, Price, Stock)
VALUES ('B0','London to Paris', 100, 22);

INSERT INTO TICKETS(ID, ProductName, Price, Stock)
VALUES ('B1','London to Berlin', 150, 11);

INSERT INTO TICKETS(ID, ProductName, Price, Stock)
VALUES ('B2','London to Madrit', 180, 150);

INSERT INTO TICKETS(ID, ProductName, Price, Stock)
VALUES ('B3','London to Roma', 500, 24);


