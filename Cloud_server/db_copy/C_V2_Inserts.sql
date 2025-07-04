CREATE OR REPLACE FUNCTION log_action(
    p_message VARCHAR,
    p_source_ip VARCHAR
)
RETURNS TEXT AS $$
BEGIN
    INSERT INTO Logs(message, time_stamp, source_ip) VALUES (p_message, NOW(), p_source_ip);
    RETURN 'Log entry created';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION add_user (
    p_username VARCHAR,
    p_password TEXT,
    p_email VARCHAR,
    p_registration_key VARCHAR,
    p_source_ip VARCHAR
)
RETURNS TEXT AS $$
DECLARE
    v_user_id INT;
    v_key_id INT;
BEGIN
    SELECT ID INTO v_user_id FROM Users WHERE username = p_username;
    IF v_user_id IS NOT NULL THEN
        PERFORM log_action(FORMAT('An user tried to register with an existing username %s', p_username), p_source_ip);
        RETURN 'Username already exists';
    END IF;

    SELECT ID INTO v_user_id FROM Users WHERE email = p_email;
    IF v_user_id IS NOT NULL THEN
        PERFORM log_action(FORMAT('An user tried to register with an existing email %s', p_email), p_source_ip);
        RETURN 'Email already exists';
    END IF;

    SELECT ID INTO v_key_id FROM Keys WHERE key = p_registration_key AND is_used = FALSE;
    IF v_key_id IS NULL THEN
        PERFORM log_action(FORMAT('An user tried to register with an invalid key %s', p_registration_key), p_source_ip);
        RETURN 'Invalid registration key';
    END IF;

    INSERT INTO Users (username, password, email, role) VALUES (p_username, p_password, p_email, 'user');

    UPDATE Keys SET is_used = TRUE, used_by = (SELECT ID FROM Users WHERE username = p_username) WHERE ID = v_key_id;

    PERFORM log_action(FORMAT('User %s registered successfully', p_username), p_source_ip);

    RETURN 'User registered successfully';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION add_key (
    p_key VARCHAR,
    p_created_by VARCHAR,
    p_source_ip VARCHAR
)
RETURNS TEXT AS $$
DECLARE
    v_user_id INT;
    v_role VARCHAR;
BEGIN
    SELECT ID, role INTO v_user_id, v_role FROM Users WHERE username = p_created_by;
    IF v_user_id IS NULL THEN
        PERFORM log_action(FORMAT('An user tried to create a key with an invalid username %s', p_created_by), p_source_ip);
        RETURN 'Invalid username';
    END IF;

    IF v_role != 'admin' THEN
        PERFORM log_action(FORMAT('An user tried to create a key without admin privileges %s', p_created_by), p_source_ip);
        RETURN 'User does not have admin privileges';
    END IF;

    INSERT INTO Keys (key, created_by, created_at) VALUES (p_key, v_user_id, NOW());

    PERFORM log_action(FORMAT('Key %s created successfully', p_key), p_source_ip);

    RETURN 'Key created successfully';
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION add_refresh_token (
    p_username VARCHAR,
    p_refresh_token VARCHAR,
    p_expires_at TIMESTAMP,
    p_source_ip VARCHAR
)
RETURNS TEXT AS $$
DECLARE
    v_user_id INT;
    v_refresh_token_id INT;
BEGIN

SELECT ID INTO v_user_id 
FROM Users 
WHERE username = p_username;

IF v_user_id IS NULL THEN
    PERFORM log_action(FORMAT('An user tried to add a refresh token with an invalid username %s', p_username), p_source_ip);
    RETURN 'Invalid username';
END IF;

SELECT ID INTO v_refresh_token_id 
FROM refresh_tokens 
WHERE user_id = v_user_id AND expires_at > NOW();

IF v_refresh_token_id IS NOT NULL THEN
    PERFORM log_action(FORMAT('An user tried to add a refresh token with an valid refresh token %s', p_username), p_source_ip);
    RETURN 'User already has a refresh token';
END IF;

INSERT INTO refresh_tokens (user_id, token_hash, expires_at)
VALUES (v_user_id, p_refresh_token, p_expires_at);

PERFORM log_action(FORMAT('Refresh token added successfully for user %s', p_username), p_source_ip);

RETURN 'Refresh token added successfully';
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION add_city_with_hierarchy (
    p_username VARCHAR,
    p_country_name VARCHAR,
    p_country_code VARCHAR,
    p_county_name VARCHAR,
    p_city_name VARCHAR,
    p_lat DECIMAL,
    p_lon DECIMAL,
    p_source_ip VARCHAR
)
RETURNS TEXT AS $$
DECLARE
    v_country_id INT;
    v_county_id INT;
    v_city_id INT;
    v_user_id INT;
BEGIN
    -- Get user ID
    SELECT id INTO v_user_id FROM Users WHERE username = p_username;
    IF v_user_id IS NULL THEN
        PERFORM log_action(FORMAT('Invalid username %s when adding city', p_username), p_source_ip);
        RETURN 'Invalid username';
    END IF;

    -- Insert or get Country
    SELECT id INTO v_country_id
    FROM Countries
    WHERE country_name = p_country_name;

    IF v_country_id IS NULL THEN
        INSERT INTO Countries (country_name, country_code)
        VALUES (p_country_name, p_country_code)
        RETURNING id INTO v_country_id;
        PERFORM log_action(FORMAT('Country %s inserted', p_country_name), p_source_ip);
    END IF;

    -- Insert or get County
    SELECT id INTO v_county_id
    FROM Counties
    WHERE county_name = p_county_name AND country_id = v_country_id;

    IF v_county_id IS NULL THEN
        INSERT INTO Counties (county_name, country_id)
        VALUES (p_county_name, v_country_id)
        RETURNING id INTO v_county_id;
        PERFORM log_action(FORMAT('County %s inserted under %s', p_county_name, p_country_name), p_source_ip);
    END IF;

    -- Check if city exists already
    SELECT id INTO v_city_id
    FROM Cities
    WHERE city_name = p_city_name AND county_id = v_county_id;

    IF v_city_id IS NOT NULL THEN
        PERFORM log_action(FORMAT('City %s already exists in county %s', p_city_name, p_county_name), p_source_ip);
        RETURN 'City already exists';
    END IF;

    -- Insert City
    INSERT INTO Cities (city_name, county_id, lat, lon)
    VALUES (p_city_name, v_county_id, p_lat, p_lon)
    RETURNING id INTO v_city_id;

    PERFORM log_action(FORMAT('City %s inserted under county %s', p_city_name, p_county_name), p_source_ip);

    -- Add entry to CityManagers
    INSERT INTO CityManagers (user_id, city_id, start_date)
    VALUES (v_user_id, v_city_id, CURRENT_DATE);

    PERFORM log_action(FORMAT('User %s assigned as manager for city %s', p_username, p_city_name), p_source_ip);

    RETURN 'City added successfully';
END;
$$ LANGUAGE plpgsql;
