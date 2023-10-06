-- Insert data into reservation_status table
INSERT INTO reservation_status (id, status_value) VALUES (1, 'Active');
INSERT INTO reservation_status (id, status_value) VALUES (2, 'Cancelled');

-- Insert data into category table
INSERT INTO category (id, category_name) VALUES (1, 'Fiction');
INSERT INTO category (id, category_name) VALUES (2, 'Non-Fiction');

-- Insert data into book table
INSERT INTO book (id, title, category_id, publication_date, copies_owned) VALUES (1, 'Sample Fiction Book', 1, TO_DATE('2023-01-01', 'YYYY-MM-DD'), 100);
INSERT INTO book (id, title, category_id, publication_date, copies_owned) VALUES (2, 'Sample Non-Fiction Book', 2, TO_DATE('2023-02-01', 'YYYY-MM-DD'), 150);

-- Insert data into author table
INSERT INTO author (id, first_name, last_name) VALUES (1, 'John', 'Doe');
INSERT INTO author (id, first_name, last_name) VALUES (2, 'Jane', 'Smith');

-- Insert data into book_author table
INSERT INTO book_author (book_id, author_id) VALUES (1, 1);
INSERT INTO book_author (book_id, author_id) VALUES (2, 2);

-- Insert data into member_status table
INSERT INTO member_status (id, status_value) VALUES (1, 'Active');
INSERT INTO member_status (id, status_value) VALUES (2, 'Inactive');

-- Insert data into member table
INSERT INTO member (id, first_name, last_name, joined_date, active_status_id) VALUES (1, 'Alice', 'Johnson', TO_DATE('2022-01-15', 'YYYY-MM-DD'), 1);
INSERT INTO member (id, first_name, last_name, joined_date, active_status_id) VALUES (2, 'Bob', 'Smith', TO_DATE('2021-11-20', 'YYYY-MM-DD'), 2);

-- Insert data into reservation table
INSERT INTO reservation (id, book_id, member_id, reservation_date, reservation_status_id) VALUES (1, 1, 1, TO_DATE('2023-03-10', 'YYYY-MM-DD'), 1);
INSERT INTO reservation (id, book_id, member_id, reservation_date, reservation_status_id) VALUES (2, 2, 2, TO_DATE('2023-03-12', 'YYYY-MM-DD'), 1);

-- Insert data into fine_payment table
INSERT INTO fine_payment (id, member_id, payment_date, payment_amount) VALUES (1, 1, TO_DATE('2023-03-15', 'YYYY-MM-DD'), 10);
INSERT INTO fine_payment (id, member_id, payment_date, payment_amount) VALUES (2, 2, TO_DATE('2023-03-16', 'YYYY-MM-DD'), 15);

-- Insert data into loan table
INSERT INTO loan (id, book_id, member_id, loan_date, returned_date) VALUES (1, 1, 1, TO_DATE('2023-02-20', 'YYYY-MM-DD'), TO_DATE('2023-03-05', 'YYYY-MM-DD'));
INSERT INTO loan (id, book_id, member_id, loan_date, returned_date) VALUES (2, 2, 2, TO_DATE('2023-01-25', 'YYYY-MM-DD'), TO_DATE('2023-02-10', 'YYYY-MM-DD'));

-- Insert data into fine table
INSERT INTO fine (id, book_id, loan_id, fine_date, fine_amount) VALUES (1, 1, 1, TO_DATE('2023-03-08', 'YYYY-MM-DD'), 5);
INSERT INTO fine (id, book_id, loan_id, fine_date, fine_amount) VALUES (2, 2, 2, TO_DATE('2023-02-28', 'YYYY-MM-DD'), 8);
