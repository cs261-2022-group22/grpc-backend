INSERT INTO BusinessSector VALUES(1, 'Private Bank');
INSERT INTO Account(name, email, passwordHash, dob, businessSectorId) 
VALUES('John Doe', 'test@gmail.com', 
E'\\x243262243132245159367569413552717a613166754f4b533478524c4f5041724a33645270774970376f334e703671324f44524c4859424256755632', 
DATE '1999-01-01', 1);