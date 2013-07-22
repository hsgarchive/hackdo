-- MySQL script to create the user and database needed to deploy the application

DROP DATABASE IF EXISTS hackdo;
DROP DATABASE IF EXISTS hackdo_test;
CREATE DATABASE hackdo COLLATE utf8_general_ci;
CREATE DATABASE test_hackdo COLLATE utf8_general_ci;

-- Change password before run this script
GRANT ALL ON hackdo.* TO 'hackdo'@'localhost' IDENTIFIED BY 'password';
GRANT ALL ON test_hackdo.* TO 'hackdo'@'localhost';
GRANT ALL PRIVILEGES ON  `hackdo\_%` . * TO  'hackdo'@'localhost';
GRANT ALL PRIVILEGES ON  `test_hackdo\_%` . * TO  'hackdo'@'localhost';
