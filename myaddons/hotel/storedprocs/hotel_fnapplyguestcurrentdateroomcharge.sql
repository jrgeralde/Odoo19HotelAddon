CREATE OR REPLACE FUNCTION hotel_fnapplyguestcurrentdateroomCharge(
    reg_id BIGINT,
    cmp_id BIGINT,
    dtapplied VARCHAR,
    detailstr VARCHAR
)
RETURNS TABLE (
    rid INT
)
AS $$
DECLARE 
    troom_id       BIGINT;
    troomtype_id   BIGINT;
    cdate          DATE;
    chargecount    INTEGER;
    result         INTEGER := 0;
    doctype_id     BIGINT;
    nextn          BIGINT;
    writedate      TIMESTAMP := now(); -- Kept this for create_date
BEGIN
   -- 1. Get room id
   SELECT room_id INTO troom_id 
   FROM hotel_guestregistration 
   WHERE id = reg_id;

   -- 2. Get room type id
   SELECT roomtype_id INTO troomtype_id 
   FROM hotel_rooms 
   WHERE id = troom_id AND company_id = cmp_id;

   -- 3. Set current date from input
   cdate := dtapplied::DATE;

   -- 4. Check if room charge already applied for current date to avoid double charging
   SELECT COUNT(*) INTO chargecount 
   FROM hotel_roombill rb
   JOIN hotel_documents d ON rb.document_id = d.id
   WHERE rb.guestregistration_id = reg_id 
     AND rb.dateapplied = cdate 
     AND rb.state = 'FINAL'
     AND d.name = 'RC';

   IF chargecount = 0 THEN
      -- Get doctype_id from hotel_documents
      SELECT id INTO doctype_id 
      FROM hotel_documents 
      WHERE name = 'RC';

      -- Get next number
      SELECT nextnum INTO nextn 
      FROM public.hotel_fnGetDocno(cmp_id, 'RC');

      -- 5. Insert room charge record
      INSERT INTO hotel_roombill(
        guestregistration_id,
        guestregistration_id_copy,
        company_id,
        charge_id,
        document_id,
        documentno,
        amountapplied,
        dateapplied,
        state,
        details,
        create_uid,
        create_date,
        write_uid,
        write_date
      )
      SELECT 
        reg_id,
        reg_id,    
        cmp_id,      
        dc.charge_id,
        doctype_id,
        nextn,
        CASE 
             WHEN EXTRACT(DOW FROM cdate) IN (0, 6) THEN dc.weekendrate 
             ELSE dc.dailyrate 
        END,
        cdate,
        'FINAL',
        detailstr,
        1,          -- Hardcoded 1 for create_uid, system user
        writedate,
        1,          -- Hardcoded 1 for write_uid, system user
        now()
      FROM hotel_dailycharges dc 
      WHERE dc.roomtype_id = troomtype_id;

      -- Check if the insert actually happened (if dailycharges had a match)
      IF FOUND THEN
          result := 1;
      END IF;
   END IF;

   -- 6. Return result (0 = no charge, 1 = applied)
   RETURN QUERY SELECT result;
END;
$$ LANGUAGE plpgsql;