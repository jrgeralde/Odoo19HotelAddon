CREATE OR REPLACE FUNCTION hotel_fnCheck_RegistrationConflict(reg_id BIGINT, cmp_id BIGINT)
RETURNS TABLE (
    rid INT,
    rmessage VARCHAR   
) AS $$
DECLARE 
    v_date_from TIMESTAMP;
    v_date_to TIMESTAMP;
    v_room_id BIGINT;
    v_conflict_exists BOOLEAN;
BEGIN
    -- 1. Get the schedule and room for the current registration
    SELECT room_id, datefromsched, datetosched
    INTO v_room_id, v_date_from, v_date_to   
    FROM hotel_guestregistration 
    WHERE id = reg_id;

    -- 2. Check for conflicts using the OVERLAPS operator
    -- This checks if any other record for the same room and company 
    -- overlaps with our time slot.
    SELECT EXISTS (
        SELECT 1
        FROM hotel_guestregistration 
        WHERE company_id = cmp_id 
          AND room_id = v_room_id 
          AND state IN ('RESERVED', 'CHECKEDIN')
          AND id <> reg_id
          AND (datefromsched, datetosched) OVERLAPS (v_date_from, v_date_to)
    ) INTO v_conflict_exists;

    -- 3. Return the result
    IF v_conflict_exists THEN
        RETURN QUERY SELECT 1, CAST('Schedule conflict exists!' AS VARCHAR);
    ELSE
        RETURN QUERY SELECT 0, CAST('No schedule conflict found' AS VARCHAR);
    END IF;

END;
$$ LANGUAGE plpgsql;