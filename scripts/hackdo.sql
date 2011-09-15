# MySQL script to create the user and database needed to deploy the application


CREATE USER 'hackdo'@'localhost' IDENTIFIED BY 'hackdo';
CREATE DATABASE IF NOT EXISTS hackdo COLLATE utf8_general_ci;
GRANT ALL ON hackdo.* TO 'hackdo'@'localhost';
GRANT ALL PRIVILEGES ON  `hackdo\_%` . * TO  'hackdo'@'localhost';
