CREATE TABLE reservation_status (
  id NUMBER(10),
  status_value VARCHAR2(50),
  CONSTRAINT pk_res_status PRIMARY KEY (id)
);

CREATE TABLE category (
  id NUMBER(10),
  category_name VARCHAR2(100),
  CONSTRAINT pk_category PRIMARY KEY (id)
);

CREATE TABLE book (
  id NUMBER(10),
  title VARCHAR2(500),
  category_id NUMBER(10),
  publication_date DATE,
  copies_owned NUMBER(10),
  CONSTRAINT pk_book PRIMARY KEY (id),
  CONSTRAINT fk_book_category FOREIGN KEY (category_id) REFERENCES category(id)
);

CREATE TABLE author (
  id NUMBER(10),
  first_name VARCHAR2(300),
  last_name VARCHAR2(300),
  CONSTRAINT pk_author PRIMARY KEY (id)
);

CREATE TABLE book_author (
  book_id NUMBER(10),
  author_id NUMBER(10),
  CONSTRAINT fk_bookauthor_book FOREIGN KEY (book_id) REFERENCES book(id),
  CONSTRAINT fk_bookauthor_author FOREIGN KEY (author_id) REFERENCES author(id)
);

CREATE TABLE member_status (
  id NUMBER(10),
  status_value VARCHAR2(50),
  CONSTRAINT pk_memberstatus PRIMARY KEY (id)
);

CREATE TABLE member (
  id NUMBER(10),
  first_name VARCHAR2(300),
  last_name VARCHAR2(300),
  joined_date DATE,
  active_status_id NUMBER(10),
  CONSTRAINT pk_member PRIMARY KEY (id),
  CONSTRAINT fk_member_status FOREIGN KEY (active_status_id) REFERENCES member_status(id)
);

CREATE TABLE reservation (
  id NUMBER(10),
  book_id NUMBER(10),
  member_id NUMBER(10),
  reservation_date DATE,
  reservation_status_id NUMBER(10),
  CONSTRAINT pk_reservation PRIMARY KEY (id),
  CONSTRAINT fk_res_book FOREIGN KEY (book_id) REFERENCES book(id),
  CONSTRAINT fk_res_member FOREIGN KEY (member_id) REFERENCES member(id)
);

CREATE TABLE fine_payment (
  id NUMBER(10),
  member_id NUMBER(10),
  payment_date DATE,
  payment_amount NUMBER(10),
  CONSTRAINT pk_fine_payment PRIMARY KEY (id),
  CONSTRAINT fk_finepay_member FOREIGN KEY (member_id) REFERENCES member(id)
);

CREATE TABLE loan (
  id NUMBER(10),
  book_id NUMBER(10),
  member_id NUMBER(10),
  loan_date DATE,
  returned_date DATE,
  CONSTRAINT pk_loan PRIMARY KEY (id),
  CONSTRAINT fk_loan_book FOREIGN KEY (book_id) REFERENCES book(id),
  CONSTRAINT fk_loan_member FOREIGN KEY (member_id) REFERENCES member(id)
);

CREATE TABLE fine (
  id NUMBER(10),
  book_id NUMBER(10),
  loan_id NUMBER(10),
  fine_date DATE,
  fine_amount NUMBER(10),
  CONSTRAINT pk_fine PRIMARY KEY (id),
  CONSTRAINT fk_fine_book FOREIGN KEY (book_id) REFERENCES book(id),
  CONSTRAINT fk_fine_loan FOREIGN KEY (loan_id) REFERENCES loan(id)
);
