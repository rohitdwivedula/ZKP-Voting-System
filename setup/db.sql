# MySQL Database setup 

CREATE DATABASE blockchain;

USE blockchain;

CREATE TABLE users(
	username varchar(25),
	password varchar(25) NOT NULL,
	rsa_public_key blob,
	rsa_private_key blob,
	PRIMARY KEY (username)
);

CREATE TABLE nodes(
	port int PRIMARY KEY,
	blockchain TEXT
);