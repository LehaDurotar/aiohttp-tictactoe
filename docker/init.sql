CREATE USER tictac WITH password 'postgres';
CREATE DATABASE tictactoedev_db;
GRANT ALL PRIVILEGES ON DATABASE tictactoedev_db TO tictac;