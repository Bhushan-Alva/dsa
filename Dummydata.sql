-- Generate 15 rows for reservation_status table
INSERT INTO reservation_status (id, status_value)
SELECT LEVEL, 'Status ' || LEVEL
FROM DUAL
CONNECT BY LEVEL <= 15;

-- Generate 15 rows for category table
INSERT INTO category (id, category_name)
SELECT LEVEL, 'Category ' || LEVEL
FROM DUAL
CONNECT BY LEVEL <= 15;

-- Generate 15 rows for book table
INSERT INTO book (id, title, category_id, publication_date, copies_owned)
SELECT LEVEL, 'Book ' || LEVEL, MOD(LEVEL, 2) + 1, SYSDATE - LEVEL, LEVEL * 10
FROM DUAL
CONNECT BY LEVEL <= 15;

-- Generate 15 rows for author table
INSERT INTO author (id, first_name, last_name)
SELECT LEVEL, 'AuthorFirstName ' || LEVEL, 'AuthorLastName ' || LEVEL
FROM DUAL
CONNECT BY LEVEL <= 15;

-- Generate 15 rows for book_author table
INSERT INTO book_author (book_id, author_id)
SELECT MOD(LEVEL, 15) + 1, MOD(LEVEL, 15) + 1
FROM DUAL
CONNECT BY LEVEL <= 15;

-- Generate 15 rows for member_status table
INSERT INTO member_status (id, status_value)
SELECT LEVEL, 'MemberStatus ' || LEVEL
FROM DUAL
CONNECT BY LEVEL <= 15;

-- Generate 15 rows for member table
INSERT INTO member (id, first_name, last_name, joined_date, active_status_id)
SELECT LEVEL, 'MemberFirstName ' || LEVEL, 'MemberLastName ' || LEVEL, SYSDATE - LEVEL, MOD(LEVEL, 2) + 1
FROM DUAL
CONNECT BY LEVEL <= 15;

-- Generate 15 rows for reservation table
INSERT INTO reservation (id, book_id, member_id, reservation_date, reservation_status_id)
SELECT LEVEL, MOD(LEVEL, 15) + 1, MOD(LEVEL, 15) + 1, SYSDATE - LEVEL, MOD(LEVEL, 15) + 1
FROM DUAL
CONNECT BY LEVEL <= 15;

-- Generate 15 rows for fine_payment table
INSERT INTO fine_payment (id, member_id, payment_date, payment_amount)
SELECT LEVEL, MOD(LEVEL, 15) + 1, SYSDATE - LEVEL, LEVEL * 5
FROM DUAL
CONNECT BY LEVEL <= 15;

-- Generate 15 rows for loan table
INSERT INTO loan (id, book_id, member_id, loan_date, returned_date)
SELECT LEVEL, MOD(LEVEL, 15) + 1, MOD(LEVEL, 15) + 1, SYSDATE - LEVEL, SYSDATE - LEVEL + 5
FROM DUAL
CONNECT BY LEVEL <= 15;

-- Generate 15 rows for fine table
INSERT INTO fine (id, book_id, loan_id, fine_date, fine_amount)
SELECT LEVEL, MOD(LEVEL, 15) + 1, MOD(LEVEL, 15) + 1, SYSDATE - LEVEL, LEVEL * 2
FROM DUAL
CONNECT BY LEVEL <= 15;
