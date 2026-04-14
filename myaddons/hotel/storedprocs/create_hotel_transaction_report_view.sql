CREATE OR REPLACE PROCEDURE create_hotel_transaction_report_view(
    date_from DATE, 
    date_to DATE, 
    cid INTEGER
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Drop the view if it exists
    DROP VIEW IF EXISTS hotel_transaction_report;

    -- Create the view
    -- Note: We use '''' to represent a single quote inside the format string
    EXECUTE format('
        CREATE OR REPLACE VIEW hotel_transaction_report AS (
            SELECT 
                hr.id,  
                hr.guestregistration_id_copy as grc_id,
                hr.document_id,
                hd.name as doc,
                hr.dateapplied,
                hr.documentno,
                hr.details,
                hr.charge_id,
                c.name as accounttitle,
                hr.amountapplied,
                hr.state,
                CASE WHEN hr.document_id IN (3,5) AND hr.state = ''FINAL'' THEN COALESCE(hr.amountapplied,0) ELSE 0.00 END as debit_amt,
                CASE WHEN hr.document_id NOT IN (3,5) AND hr.state = ''FINAL'' THEN COALESCE(hr.amountapplied,0) ELSE 0.00 END as credit_amt,
                CONCAT(
                    COALESCE(hgt.lastname, ''''), '', '', 
                    COALESCE(hgt.firstname, ''''), '' '', 
                    COALESCE(hgt.middlename, '''')
                ) as guestname,
                hm.name as roomname,
                hrt.name as roomtypename,
                hg.state as staystatus,
                hr.company_id,
                ROW_NUMBER() OVER (ORDER BY c.name,hr.dateapplied) AS line_no
            FROM hotel_roombill hr
            LEFT JOIN hotel_documents hd ON hr.document_id = hd.id
            LEFT JOIN hotel_charges c ON hr.charge_id = c.id
            LEFT JOIN hotel_guestregistration hg ON hr.guestregistration_id_copy = hg.id
            LEFT JOIN hotel_guests hgt ON hg.guest_id = hgt.id
            LEFT JOIN hotel_rooms hm ON hg.room_id = hm.id
            LEFT JOIN hotel_roomtypes hrt ON hm.roomtype_id = hrt.id
            WHERE (hr.dateapplied BETWEEN %L AND %L) AND hr.company_id = %s
        )', date_from, date_to, cid);
END;
$$;
