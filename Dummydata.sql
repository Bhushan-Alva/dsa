1.
CREATE or REPLACE procedure payment_details(
	rent_id number) is
	type rec_type is record
	(c_id customers.customer_id%type,
	c_name customers.customer_name%type,
	r_pay rent_payment.payment%type,
	m_pay mod_pay.mod_payment%type,
	total number);
	type rec is  table of rec_type ;
	payment rec;
BEGIN
	SELECT  c.customer_id, c.customer_name,
	r.payment, m.mod_payment, (r.payment+m.mod_payment) as total
	bulk collect into payment
	FROM rent_payment r
	JOIN customers c on(r.customer_id=c.customer_id)
	JOIN mod_pay m on (r.mod_id=m.mod_id)
	WHERE rental_id=rent_id;
	for i in payment.first..payment.last loop
	dbms_output.put_line('Customer id: ' ||  payment(i).c_id || '
' || 'Customer name: ' ||  payment(i).c_name || '
' || 'Rent Amount: ' ||  payment(i).r_pay || '
' || 'Fine: ' ||  payment(i).m_pay || '
' || 'Total amount: ' ||  payment(i).total);
	END loop;
EXCEPTION
	when others then
        dbms_output.put_line('No record found');
END payment_details;
/

************************************************************************
2.
create or replace function get_receipt (
cust_id number) return varchar2 is
cursor c1 is select rp.rental_id as r_id, c.customer_id as c_id, c.customer_name as c_name, rp.payment as r_pay, mp.mod_payment as m_pay, (rp.payment+mp.mod_payment) as total, rent_srt_date as rsd, rent_ret_date as rrd
	from rent_payment rp
	join rentals r on(r.rental_id=rp.rental_id)
	join customers c on(rp.customer_id=c.customer_id)
	join mod_pay mp on (rp.mod_id=mp.mod_id)
	where c.customer_id=cust_id;
v_rec c1%rowtype;
receipt varchar2(30000);
begin
open c1;
loop
fetch c1 into v_rec;
exit when c1%notfound;
receipt := 'Rental id: ' || v_rec.r_id || '
' || 'Customer id: ' || v_rec.c_id || '
' || 'Customer name: ' || v_rec.c_name || '
' || 'Rent amount: ' || v_rec.r_pay || '
' || 'extras: ' || v_rec.m_pay || '
' || 'Total amount: ' || v_rec.total || '
' || 'Rent start date: ' || v_rec.rsd || '
' || 'Rent return date: ' || v_rec.rrd || '
*******************
';
end loop;
close c1;
return receipt;
end get_receipt;
/
**************************************************************************

4.
DECLARE
	y number := &year;
	m_cust_id number;
BEGIN
	SELECT customer_id into m_cust_id 
	FROM (select customer_id, to_char(rent_srt_date, 'yyyy') as year, count(customer_id) 
	FROM rentals  group by customer_id, to_char(rent_srt_date, 'yyyy') 
	ORDER BY count(customer_id) desc, to_char(rent_srt_date, 'yyyy')) 
	WHERE year=y and rownum=1;
	DECLARE
		CURSOR c1 is 
		SELECT c.customer_id as c_id, c.customer_name as c_name, r.rental_id as r_id, r.rent_srt_date as rsd 
		FROM customers c JOIN rentals r on(c.customer_id=r.customer_id) 
		WHERE c.customer_id=m_cust_id and to_char(r.rent_srt_date, 'yyyy')=y;
		v_rec c1%rowtype;
	BEGIN
		open c1;
		loop
		fetch c1 into v_rec;
		exit when c1%notfound;
		dbms_output.put_line(v_rec.c_id || ' ' || v_rec.r_id || ' ' ||v_rec.c_name || ' ' ||v_rec.rsd);
		end loop;
		close c1;
	END;
EXCEPTION
	when no_data_found then
	dbms_output.put_line('No record found');
END;
/

***********************************************************************
5.
CREATE or REPLACE procedure month_rentals (
	p_agency varchar2,
	p_date varchar2) is
	type rec_type is record (
		r_id rent_payment.rental_id%type,
		c_id customers.customer_id%type,
		c_name customers.customer_name%type,
		a_id agency.agency_id%type,
		rsd date);
	type result_tab is table of rec_type;
	v_rec result_tab;
BEGIN
	SELECT r.rental_id, r.customer_id, c.customer_name, r.agency_id, r.rent_srt_date BULK COLLECT into v_rec
	FROM rentals r
	JOIN customers c on (r.customer_id=c.customer_id)
	JOIN agency a on(c.agency_id=a.agency_id)
	WHERE a.agency_loc=p_agency and to_char(rent_srt_date, 'mon-yyyy')=p_date;
	for i in v_rec.first..v_rec.last loop
	dbms_output.put_line(
'Rental id: ' || v_rec(i).r_id || '
' || 'Customer id: ' || v_rec(i).c_id || '
' || 'Customer name: ' || v_rec(i).c_name || '
' || 'Agency id: ' || v_rec(i).a_id || '
' || 'Rent start date: ' || v_rec(i).rsd || '
*******
');
	end loop;
END month_rentals;
/

*************************************************************************
3.
DECLARE
	y number;
	type rec_type is record (
		a_loc agency.agency_loc%type,
		c_name varchar(20),
		ct number);
	type rec is  table of rec_type;
	v_rec rec;
BEGIN
	SELECT a.agency_loc,to_char(rent_srt_date, 'yyyy') as year, 
	count(a.agency_id) as count bulk collect into v_rec 
	FROM agency a JOIN rentals r on(a.agency_id=r.agency_id) 
	WHERE to_char(rent_srt_date, 'yyyy')=&y 
	GROUP BY (to_char(rent_srt_date, 'yyyy'), 
	a.agency_loc);
	for i in v_rec.first..v_rec.last loop
	dbms_output.put_line(v_rec(i).a_loc || ': ' || v_rec(i).ct);
	end loop;
END;
/

*************************************************************************
6. with modification detals table (track_table)

*********
create table track_table(sno number, customer_id number, old_phone_num number, new_phone_num number, status varchar2(30), mod_date date);
*********
create sequence s1;
*********
CREATE or REPLACE procedure update_track_table(o_pno number, n_pno number, c_id number)  is
	pragma autonomous_transaction ;
BEGIN
	insert into track_table values ( s1.nextval, c_id, o_pno, n_pno, 'Data updated', sysdate);
	commit;
END update_track_table;
/


********

CREATE or REPLACE trigger check_num
	before insert or update on customers for each row
DECLARE
	old_pno number;
	new_pno number;
	c_id number;

BEGIN
	if (length(:new.customer_number) != 10) then
		raise_application_error(-20555, 'THe phone number should contain 10 digits');
	else
		old_pno:=:old.customer_number;
		new_pno:=:new.customer_number;
		c_id:=:new.customer_id;
		update_track_table(old_pno, new_pno, c_id);
	end if;
END check_num;
/


********************************************************************

SELECT a.agency_loc,to_char(rent_srt_date, 'yyyy') as year, count(a.agency_id) 
FROM agency a 
JOIN rentals r on(a.agency_id=r.agency_id) 
GROUP BY rollup(to_char(rent_srt_date, 'yyyy'), a.agency_loc);


















