CREATE OR REPLACE FUNCTION log_action(
    p_action_type VARCHAR,
    p_user_id INT,
    p_message VARCHAR,
    p_source_ip VARCHAR
    )
    RETURNS TEXT AS $$
    BEGIN
        IF p_action_type NOT IN ('login', 'registration', 'key generation', 'cities','etc', 'device') THEN
            RAISE EXCEPTION 'Invalid action_type: %', p_action_type;
        END IF;

        INSERT INTO Logs(action_type, user_id, message, time_stamp, source_ip)
        VALUES (p_action_type, p_user_id, p_message, NOW(), p_source_ip);

        RETURN 'Log entry created';
    END;
    $$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION add_key (
    p_user_id INT,
    p_admin_username VARCHAR,
    p_key VARCHAR,
    p_source_ip VARCHAR
    )
    RETURNS TEXT AS $$
    DECLARE
        v_admin_id INT;
        v_admin_role VARCHAR;
        v_existing_key_id INT;
    BEGIN
        -- Verificăm dacă utilizatorul care creează cheia (adminul) există
        SELECT ID, role INTO v_admin_id, v_admin_role
        FROM Users
        WHERE username = p_admin_username;

        IF v_admin_id IS NULL THEN
            PERFORM log_action('key generation', NULL, FORMAT('Attempted key creation with invalid admin username: %s', p_admin_username), p_source_ip);
            RETURN 'Invalid admin username';
        END IF;

        -- Verificăm dacă are drepturi de admin
        IF v_admin_role <> 'admin' THEN
            PERFORM log_action('key generation', v_admin_id, FORMAT('User %s tried to create a key without admin privileges', p_admin_username), p_source_ip);
            RETURN 'User is not admin';
        END IF;

        -- Verificăm dacă utilizatorul pentru care se creează cheia există
        IF NOT EXISTS (SELECT 1 FROM Users WHERE ID = p_user_id) THEN
            PERFORM log_action('key generation', v_admin_id, FORMAT('Attempted to assign key to invalid user ID: %s', p_user_id), p_source_ip);
            RETURN 'Target user not found';
        END IF;

        -- Verificăm dacă deja are o cheie (nefolosită și neexpirată)
        SELECT key_id
        INTO v_existing_key_id
        FROM Users
        WHERE ID = p_user_id AND key_id IS NOT NULL;


        IF v_existing_key_id IS NOT NULL THEN
            PERFORM log_action('key generation', v_admin_id, FORMAT('User ID %s already has a key assigned', p_user_id), p_source_ip);
            RETURN 'User already has a key';
        END IF;

        -- Inserăm cheia
        INSERT INTO Keys (key, created_by, created_at, expires_at)
        VALUES (p_key, v_admin_id, NOW(), NOW() + INTERVAL '1 hour');

        -- Asociem cheia userului
        UPDATE Users
        SET key_id = (SELECT ID FROM Keys WHERE key = p_key)
        WHERE ID = p_user_id;

        -- Log de succes
        PERFORM log_action('key generation', v_admin_id, FORMAT('Key %s created and assigned to user ID %s', p_key, p_user_id), p_source_ip);

        RETURN 'Key created and assigned successfully';
    END;
    $$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION add_user (
    p_first_name VARCHAR,
    p_last_name VARCHAR,
    p_date_of_birth DATE,
    p_address VARCHAR,
    p_email VARCHAR,
    p_profession VARCHAR,
    p_workplace VARCHAR,
    p_phone VARCHAR,
    p_id_front VARCHAR,
    p_id_back VARCHAR,
    p_source_ip VARCHAR
    )
    RETURNS TEXT AS $$
    DECLARE
        v_user_id INT;
    BEGIN
        INSERT INTO Users (
            first_name,
            last_name,
            username,
            password,
            email,
            role,
            date_of_birth,
            address,
            profession,
            workplace,
            phone,
            id_front,
            id_back,
            created_at,
            status
        ) VALUES (
            p_first_name,
            p_last_name,
            'temp_username_' || FLOOR(RANDOM() * 1000000),
            'temp_password' || FLOOR(RANDOM() * 1000000),
            p_email,
            'pending_user',
            p_date_of_birth,
            p_address,
            p_profession,
            p_workplace,
            p_phone,
            p_id_front,
            p_id_back,
            NOW(),
            'pending'
        ) RETURNING ID INTO v_user_id;

        PERFORM log_action('registration', v_user_id, FORMAT('User pre-added'), p_source_ip);

        RETURN 'User pre-added successfully';
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
        -- Obținem ID-ul utilizatorului
        SELECT ID INTO v_user_id 
        FROM Users 
        WHERE username = p_username;

        IF v_user_id IS NULL THEN
            PERFORM log_action('login', NULL, FORMAT('Attempted to add refresh token with invalid username: %s', p_username), p_source_ip);
            RETURN 'Invalid username';
        END IF;

        -- Verificăm dacă are deja un refresh token valid
        SELECT ID INTO v_refresh_token_id 
        FROM refresh_tokens 
        WHERE user_id = v_user_id AND expires_at > NOW();

        IF v_refresh_token_id IS NOT NULL THEN
            PERFORM log_action('login', v_user_id, FORMAT('Attempted to add new refresh token while one is still valid for user: %s', p_username), p_source_ip);
            RETURN 'User already has a refresh token';
        END IF;

        -- Inserăm tokenul
        INSERT INTO refresh_tokens (user_id, token_hash, expires_at, created_at)
        VALUES (v_user_id, p_refresh_token, p_expires_at, NOW());

        -- Log
        PERFORM log_action('login', v_user_id, FORMAT('Refresh token added successfully for user: %s', p_username), p_source_ip);

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
            PERFORM log_action('cities', NULL, FORMAT('Invalid username %s when adding city', p_username), p_source_ip);
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
            PERFORM log_action('cities', v_user_id, FORMAT('Country %s inserted', p_country_name), p_source_ip);
        END IF;

        -- Insert or get County
        SELECT id INTO v_county_id
        FROM Counties
        WHERE county_name = p_county_name AND country_id = v_country_id;

        IF v_county_id IS NULL THEN
            INSERT INTO Counties (county_name, country_id)
            VALUES (p_county_name, v_country_id)
            RETURNING id INTO v_county_id;
            PERFORM log_action('cities', v_user_id, FORMAT('County %s inserted under %s', p_county_name, p_country_name), p_source_ip);
        END IF;

        -- Check if city exists already
        SELECT id INTO v_city_id
        FROM Cities
        WHERE city_name = p_city_name AND county_id = v_county_id;

        IF v_city_id IS NOT NULL THEN
            PERFORM log_action('cities', v_user_id, FORMAT('City %s already exists in county %s', p_city_name, p_county_name), p_source_ip);
            RETURN 'City already exists';
        END IF;

        -- Insert City
        INSERT INTO Cities (city_name, county_id, lat, lon)
        VALUES (p_city_name, v_county_id, p_lat, p_lon)
        RETURNING id INTO v_city_id;

        PERFORM log_action('cities', v_user_id, FORMAT('City %s inserted under county %s', p_city_name, p_county_name), p_source_ip);

        -- Add entry to CityManagers
        INSERT INTO CityManagers (user_id, city_id, start_date)
        VALUES (v_user_id, v_city_id, CURRENT_DATE);

        PERFORM log_action('cities', v_user_id, FORMAT('User %s assigned as manager for city %s', p_username, p_city_name), p_source_ip);

        RETURN 'City added successfully';
    END;
    $$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION add_device(
    p_node_name VARCHAR,
    p_city_name VARCHAR,
    p_county_name VARCHAR,
    p_country_name VARCHAR,
    p_lat DECIMAL,
    p_lon DECIMAL,
    p_ip_address VARCHAR,
    p_source_ip VARCHAR
    )
    RETURNS TEXT AS $$
    DECLARE
        v_country_id INT;
        v_county_id INT;
        v_city_id INT;
        v_node_id INT;
        v_device_exists INT;
    BEGIN
        -- Găsim orașul
        SELECT ctr.ID, co.ID, c.ID
        INTO v_country_id, v_county_id, v_city_id
        FROM Countries ctr
        JOIN Counties co ON co.country_id = ctr.ID
        JOIN Cities c ON c.county_id = co.ID
        WHERE LOWER(ctr.country_name) = LOWER(p_country_name)
        AND LOWER(co.county_name) = LOWER(p_county_name)
        AND LOWER(c.city_name) = LOWER(p_city_name)
        LIMIT 1;

        IF v_city_id IS NULL THEN
            PERFORM log_action('device', NULL, FORMAT(
                'Attempted to add device for unknown city hierarchy: %s > %s > %s',
                p_country_name, p_county_name, p_city_name
            ), p_source_ip);
            RETURN 'City/County/Country combination not found';
        END IF;

        -- Căutăm sau inserăm nodul
        SELECT ID INTO v_node_id
        FROM Nodes
        WHERE LOWER(node_name) = LOWER(p_node_name)
        AND city_id = v_city_id;

        IF v_node_id IS NULL THEN
            INSERT INTO Nodes (node_name, city_id)
            VALUES (p_node_name, v_city_id)
            RETURNING ID INTO v_node_id;

            PERFORM log_action('device', NULL, FORMAT(
                'Node %s created in city %s',
                p_node_name, p_city_name
            ), p_source_ip);
        END IF;

        -- Verificăm dacă device-ul există deja
        SELECT COUNT(*) INTO v_device_exists
        FROM Devices
        WHERE lat = p_lat AND lon = p_lon AND ip_address = p_ip_address AND node_id = v_node_id;

        IF v_device_exists > 0 THEN
            PERFORM log_action('device', NULL, FORMAT(
                'Device connected: (%s, %s, %s) under node %s',
                p_lat, p_lon, p_ip_address, p_node_name
            ), p_source_ip);
            RETURN 'Device connected successfully';
        END IF;

        -- Inserăm device-ul
        INSERT INTO Devices (lat, lon, ip_address, status, node_id)
        VALUES (p_lat, p_lon, p_ip_address, 'online', v_node_id);

        PERFORM log_action('device', NULL, FORMAT(
            'Device added under node %s in city %s',
            p_node_name, p_city_name
        ), p_source_ip);

        RETURN 'Device added successfully';
    END;
    $$ LANGUAGE plpgsql;
