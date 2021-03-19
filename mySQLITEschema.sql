DROP TABLE IF EXISTS `library`.`loan`;
DROP TABLE IF EXISTS `library`.`reserve`;
DROP TABLE IF EXISTS `library`.`fine`;
DROP TABLE IF EXISTS `library`.`payment`;
DROP TABLE IF EXISTS `library`.`userTable`;

CREATE TABLE `library`.`userTable` (
  `userID` INT NOT NULL AUTO_INCREMENT,
  `userName` VARCHAR(45) NOT NULL,
  `userPassword` VARCHAR(45) NOT NULL,
  `email` VARCHAR(45) NOT NULL,
  `fName` VARCHAR(45) NOT NULL,
  `lName` VARCHAR(45) NOT NULL,
  `phoneNum` VARCHAR(45) NOT NULL,
  `blockNum` VARCHAR(45) NOT NULL,
  `streetName` VARCHAR(45) NOT NULL,
  `unitNum` VARCHAR(8) NOT NULL,
  `postalCode` CHAR(6) NOT NULL,
  `admin` BOOLEAN NOT NULL DEFAULT 0,
  PRIMARY KEY (`userID`),
  UNIQUE INDEX `userID_UNIQUE` (`userID` ASC) VISIBLE);


CREATE TABLE IF NOT EXISTS `library`.`payment` (
	`paymentID`	INTEGER UNIQUE,
	`paymentDate`	DATE,
	`paymentAmount`	INTEGER,
	`userID`	INTEGER,
	FOREIGN KEY(`userID`) REFERENCES `userTable`(`userID`),
	PRIMARY KEY(`paymentID`),
	UNIQUE INDEX `paymentID_UNIQUE` (`paymentID` ASC) VISIBLE
);


CREATE TABLE `library`.`fine` (
	`fineID`	INT NOT NULL AUTO_INCREMENT,
	`userID`	INTEGER,
	`fineCreationDate`	DATE,
	`fineAmount`	INTEGER,
	FOREIGN KEY(`userID`) REFERENCES `userTable`(`userID`),
	PRIMARY KEY(`fineID`),
	UNIQUE INDEX `fineID_UNIQUE` (`fineID` ASC) VISIBLE
	);



DROP TABLE IF EXISTS `library`.`book`;
CREATE TABLE IF NOT EXISTS `library`.`book` (
	`bookID`	INTEGER NOT NULL AUTO_INCREMENT,
	`availability`	BOOLEAN NOT NULL DEFAULT 1,
	`reservedAvailability`	BOOLEAN NOT NULL DEFAULT 1,
	PRIMARY KEY(`bookID`),
	UNIQUE INDEX `bookID_UNIQUE` (`bookID` ASC) VISIBLE
);


CREATE TABLE IF NOT EXISTS `library`.`reserve` (
	`reserveID`	INTEGER NOT NULL AUTO_INCREMENT,
	`userID`	INTEGER NOT NULL,
	`bookID`	INTEGER NOT NULL,
	`reserveDate`	DATE NOT NULL,
	`endDate`	DATE,
	FOREIGN KEY(`bookID`) REFERENCES `book`(`bookID`),
	FOREIGN KEY(`userID`) REFERENCES `userTable`(`userID`),
	PRIMARY KEY(`reserveID`),
	UNIQUE INDEX `reserveID_UNIQUE` (`reserveID` ASC) VISIBLE
);

CREATE TABLE IF NOT EXISTS `library`.`loan` (
	`loanID`	INTEGER NOT NULL AUTO_INCREMENT,
	`userID`	INTEGER NOT NULL,
	`bookID`	INTEGER NOT NULL,
	`borrowDate`	DATE NOT NULL,
	`dueDate`	DATE,
	`returnDate`	DATE,
	FOREIGN KEY(`bookID`) REFERENCES `book`(`bookID`),
	FOREIGN KEY(`userID`) REFERENCES `userTable`(`userID`),
	PRIMARY KEY(`loanID`)
);