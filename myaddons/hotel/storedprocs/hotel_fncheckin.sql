CREATE OR REPLACE FUNCTION hotel_fnCheckin(reg_id BIGINT, cmp_id BIGINT)
RETURNS TABLE (
    rid INT
)
AS $$
DECLARE 
    dtapplied     DATE;
    dtappliedstr  VARCHAR;
    result        INTEGER := 0; -- Default to 0 (failure)
    chargedroom   INTEGER;
BEGIN
    -- 1. Set current date
    dtapplied := CURRENT_DATE;
    dtappliedstr := dtapplied::VARCHAR;

    -- 2. Call the room charge function
    -- This returns 1 if a charge was inserted, 0 if it already existed or failed.
    SELECT f.rid INTO chargedroom
    FROM public.hotel_fnapplyguestcurrentdateroomCharge(reg_id, cmp_id, dtappliedstr, 'Initial check in daily room charge.') AS f;

    -- 3. Only update registration status if the room charge was successful (or already exists)
    -- If you want to allow check-in even if charge was already applied, use: IF chargedroom >= 0
    IF chargedroom = 1 THEN
        UPDATE hotel_guestregistration 
        SET state = 'CHECKEDIN',
            write_date = now()
        WHERE id = reg_id;

        -- Check if the UPDATE actually found the reg_id
        IF FOUND THEN
            result := 1;
        END IF;
    ELSE
        -- Optional: logic if the room charge failed (e.g., room type not found)
        result := 0;
    END IF;

    -- 4. Return result
    RETURN QUERY SELECT result;
END;
$$ LANGUAGE plpgsql;