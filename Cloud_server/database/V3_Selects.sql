CREATE OR REPLACE FUNCTION validate_refresh_token (
    p_username VARCHAR,
    p_refresh_token VARCHAR,
    p_source_ip VARCHAR
    )
    RETURNS BOOLEAN AS $$
    DECLARE
        v_user_id INT;
        v_refresh_token_id INT;
        v_expires_at TIMESTAMP;
    BEGIN

    SELECT ID INTO v_user_id
    FROM Users
    WHERE username = p_username;

    IF v_user_id IS NULL THEN
        PERFORM log_action('login', NULL, FORMAT('Invalid username during refresh token validation: %s', p_username), p_source_ip);
        RETURN FALSE;
    END IF;

    SELECT ID INTO v_refresh_token_id
    FROM refresh_tokens
    WHERE user_id = v_user_id AND token_hash = p_refresh_token;

    IF v_refresh_token_id IS NULL THEN
        PERFORM log_action('login', v_user_id, FORMAT('Invalid refresh token for user: %s', p_username), p_source_ip);
        RETURN FALSE;
    END IF;

    SELECT expires_at INTO v_expires_at
    FROM refresh_tokens
    WHERE ID = v_refresh_token_id;

    IF v_expires_at < NOW() THEN
        PERFORM log_action('login', v_user_id, FORMAT('Expired refresh token used by user: %s', p_username), p_source_ip);
        PERFORM revoke_refresh_token(p_username, p_source_ip);
        RETURN FALSE;
    END IF;

    PERFORM log_action('login', v_user_id, FORMAT('Valid refresh token used by user: %s', p_username), p_source_ip);
    RETURN TRUE;
    END;
    $$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_password (
    p_username VARCHAR,
    p_source_ip VARCHAR
    )
    RETURNS TEXT AS $$
    DECLARE
        v_user_id INT;
        v_password TEXT;
    BEGIN
        -- Căutăm userul după username
        SELECT ID, password INTO v_user_id, v_password
        FROM Users
        WHERE username = p_username;

        -- Dacă userul nu există
        IF v_user_id IS NULL THEN
            PERFORM log_action('login', NULL, FORMAT('Attempted login with invalid username: %s', p_username), p_source_ip);
            RETURN 'Invalid credentials';
        END IF;

        -- Logare reușită
        PERFORM log_action('login', v_user_id, FORMAT('User %s logged in successfully', p_username), p_source_ip);

        RETURN v_password;
    END;
    $$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_user(
    p_username VARCHAR,
    p_source_ip VARCHAR
    )
    RETURNS JSON AS $$
    DECLARE
        v_user_id INT;
        v_email VARCHAR;
        v_role VARCHAR;
    BEGIN
        -- Căutăm utilizatorul
        SELECT ID INTO v_user_id
        FROM Users
        WHERE username = p_username;

        -- Dacă nu există
        IF v_user_id IS NULL THEN
            PERFORM log_action('etc', NULL, FORMAT('Attempted access to user details with invalid username: %s', p_username), p_source_ip);
            RETURN json_build_object('error', 'User not found');
        END IF;

        -- Obținem restul informațiilor
        SELECT email, role INTO v_email, v_role
        FROM Users
        WHERE ID = v_user_id;

        -- Log acces
        PERFORM log_action('etc', v_user_id, FORMAT('User %s retrieved their account details', p_username), p_source_ip);

        -- Returnăm obiect JSON
        RETURN json_build_object(
            'username', p_username,
            'email', v_email,
            'role', v_role
        );

    END;
    $$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_managed_cities(
    p_username VARCHAR,
    p_source_ip VARCHAR
    )
    RETURNS JSON AS $$
    DECLARE
        v_user_id INT;
        city_rec RECORD;
        city_list JSON := '[]'::json;
    BEGIN
        -- Obținem ID-ul utilizatorului
        SELECT ID INTO v_user_id
        FROM Users
        WHERE username = p_username;

        -- Verificăm dacă utilizatorul există
        IF v_user_id IS NULL THEN
            PERFORM log_action('etc', NULL, FORMAT('Attempted to get managed cities with invalid username: %s', p_username), p_source_ip);
            RETURN json_build_object('error', 'User not found');
        END IF;

        -- Iterăm prin orașele administrate și numărăm device-urile pe status
        FOR city_rec IN
            SELECT 
                c.city_name,
                co.county_name,
                ctr.country_name,
                c.ID AS city_id,
                (
                    SELECT COUNT(*)
                    FROM Devices d
                    JOIN Nodes n ON d.node_id = n.ID
                    WHERE n.city_id = c.ID
                ) AS camera_count,
                (
                    SELECT COUNT(*)
                    FROM Devices d
                    JOIN Nodes n ON d.node_id = n.ID
                    WHERE n.city_id = c.ID AND d.status = 'online'
                ) AS online_count,
                (
                    SELECT COUNT(*)
                    FROM Devices d
                    JOIN Nodes n ON d.node_id = n.ID
                    WHERE n.city_id = c.ID AND d.status = 'offline'
                ) AS offline_count
            FROM Cities c
            JOIN Counties co ON c.county_id = co.ID
            JOIN Countries ctr ON co.country_id = ctr.ID
            JOIN CityManagers cm ON cm.city_id = c.ID
            WHERE cm.user_id = v_user_id
        LOOP
            city_list := city_list::jsonb || jsonb_build_array(
                jsonb_build_object(
                    'name', city_rec.city_name,
                    'county', city_rec.county_name,
                    'country', city_rec.country_name,
                    'cameras', city_rec.camera_count,
                    'online', city_rec.online_count,
                    'offline', city_rec.offline_count
                )
            );
        END LOOP;

        -- Log acțiunea
        PERFORM log_action('etc', v_user_id, FORMAT('User %s retrieved managed cities list', p_username), p_source_ip);

        RETURN city_list;
    END;
    $$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION get_city_coordinates(
    p_city_name VARCHAR,
    p_county_name VARCHAR,
    p_country_name VARCHAR,
    p_source_ip VARCHAR
    )
    RETURNS JSON AS $$
    DECLARE
        v_lat DECIMAL;
        v_lon DECIMAL;
    BEGIN
        -- Căutăm coordonatele
        SELECT c.lat, c.lon
        INTO v_lat, v_lon
        FROM Cities c
        JOIN Counties co ON c.county_id = co.ID
        JOIN Countries ctr ON co.country_id = ctr.ID
        WHERE LOWER(c.city_name) = LOWER(p_city_name)
        AND LOWER(co.county_name) = LOWER(p_county_name)
        AND LOWER(ctr.country_name) = LOWER(p_country_name)
        LIMIT 1;

        -- Dacă nu am găsit orașul
        IF NOT FOUND THEN
            PERFORM log_action(
                'etc',
                NULL,
                FORMAT('Attempted to get coordinates for unknown city: %s, %s, %s', p_city_name, p_county_name, p_country_name),
                p_source_ip
            );
            RETURN json_build_object('error', 'City not found');
        END IF;

        -- Logare succes
        PERFORM log_action(
            'etc',
            NULL,
            FORMAT('Fetched coordinates for city: %s, %s, %s', p_city_name, p_county_name, p_country_name),
            p_source_ip
        );

        -- Returnăm coordonatele
        RETURN json_build_object(
            'city', p_city_name,
            'county', p_county_name,
            'country', p_country_name,
            'lat', v_lat,
            'lon', v_lon
        );
    END;
    $$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_user_role(
    p_username VARCHAR,
    p_source_ip VARCHAR
    )
    RETURNS JSON AS $$
    DECLARE
        v_user_id INT;
        v_role VARCHAR;
    BEGIN
        -- Căutăm utilizatorul
        SELECT id, role INTO v_user_id, v_role
        FROM Users
        WHERE username = p_username;

        -- Nu există
        IF v_user_id IS NULL THEN
            PERFORM log_action('etc', NULL, FORMAT('Attempted to retrieve role for unknown user: %s', p_username), p_source_ip);
            RETURN json_build_object('error', 'User not found');
        END IF;

        -- Logare și returnare
        PERFORM log_action('etc', v_user_id, FORMAT('User %s retrieved their role', p_username), p_source_ip);

        RETURN json_build_object(
            'username', p_username,
            'role', v_role
        );
    END;
    $$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_pending_users (
    p_username VARCHAR,
    p_source_ip VARCHAR
    )
    RETURNS JSON AS $$
    DECLARE
        v_user_id INT;
        user_rec RECORD;
        user_list JSON := '[]'::JSON;
    BEGIN
        -- Validăm utilizatorul apelant
        SELECT ID INTO v_user_id FROM Users WHERE username = p_username AND role = 'admin';

        IF v_user_id IS NULL THEN
            PERFORM log_action('etc', NULL, FORMAT('Attempted to fetch pending users with invalid username: %s or insufficient role', p_username), p_source_ip);
            RETURN json_build_object('error', 'Invalid requester');
        END IF;

        -- Iterăm prin userii cu status = 'pending'
        FOR user_rec IN
            SELECT ID, first_name, last_name, email, created_at, date_of_birth,
            address, profession, workplace, phone, id_front, id_back
            FROM Users
            WHERE status = 'pending'
        LOOP
            user_list := user_list::jsonb || jsonb_build_array(
                jsonb_build_object(
                    'id', user_rec.id,
                    'first_name', user_rec.first_name,
                    'last_name', user_rec.last_name,
                    'date_of_birth', user_rec.date_of_birth,
                    'address', user_rec.address,
                    'profession', user_rec.profession,
                    'workplace', user_rec.workplace,
                    'phone', user_rec.phone,
                    'id_front', user_rec.id_front,
                    'id_back', user_rec.id_back,
                    'email', user_rec.email,
                    'created_at', user_rec.created_at
                )
            );
        END LOOP;

        -- Logăm acțiunea
        PERFORM log_action('etc', v_user_id, FORMAT('Fetched pending users list'), p_source_ip);

        RETURN user_list;
    END;
    $$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_city_devices(
    p_city_name VARCHAR,
    p_county_name VARCHAR,
    p_country_name VARCHAR,
    p_username VARCHAR,
    p_source_ip VARCHAR
    )
    RETURNS JSON AS $$
    DECLARE
        v_user_id INT;
        v_city_id INT;
        v_result JSON := '[]'::json;
        rec RECORD;
    BEGIN
        -- Obține ID-ul utilizatorului
        SELECT ID INTO v_user_id FROM Users WHERE username = p_username;

        IF v_user_id IS NULL THEN
            PERFORM log_action('device', NULL, FORMAT(
                'Attempted to fetch devices with invalid username %s',
                p_username
            ), p_source_ip);
            RETURN json_build_object('error', 'Invalid username');
        END IF;

        -- Verifică existența orașului
        SELECT c.ID INTO v_city_id
        FROM Cities c
        JOIN Counties co ON c.county_id = co.ID
        JOIN Countries ctr ON co.country_id = ctr.ID
        WHERE LOWER(c.city_name) = LOWER(p_city_name)
        AND LOWER(co.county_name) = LOWER(p_county_name)
        AND LOWER(ctr.country_name) = LOWER(p_country_name)
        LIMIT 1;

        IF v_city_id IS NULL THEN
            PERFORM log_action('device', v_user_id, FORMAT(
                'Attempted to fetch devices for unknown city: %s > %s > %s',
                p_country_name, p_county_name, p_city_name
            ), p_source_ip);
            RETURN json_build_object('error', 'City not found');
        END IF;

        -- Parcurgem toate device-urile asociate cu orașul
        FOR rec IN
            SELECT d.id AS device_id, d.lat, d.lon, d.ip_address, d.status,
                n.node_name
            FROM Devices d
            JOIN Nodes n ON d.node_id = n.ID
            WHERE n.city_id = v_city_id
        LOOP
            v_result := v_result::jsonb || jsonb_build_array(
                jsonb_build_object(
                    'device_id', rec.device_id,
                    'lat', rec.lat,
                    'lon', rec.lon,
                    'ip_address', rec.ip_address,
                    'status', rec.status,
                    'node_name', rec.node_name
                )
            );
        END LOOP;

        PERFORM log_action('device', v_user_id, FORMAT(
            'Fetched devices for city %s > %s > %s',
            p_country_name, p_county_name, p_city_name
        ), p_source_ip);

        RETURN v_result;
    END;
    $$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_city_online_count(
    p_country_name VARCHAR,
    p_county_name VARCHAR,
    p_city_name VARCHAR,
    p_source_ip VARCHAR
    )
    RETURNS INT AS $$
    DECLARE
        v_city_id INT;
        v_online_count INT;
    BEGIN
        -- Găsim ID-ul orașului după country > county > city
        SELECT c.ID INTO v_city_id
        FROM Cities c
        JOIN Counties co ON c.county_id = co.ID
        JOIN Countries ctr ON co.country_id = ctr.ID
        WHERE LOWER(c.city_name) = LOWER(p_city_name)
        AND LOWER(co.county_name) = LOWER(p_county_name)
        AND LOWER(ctr.country_name) = LOWER(p_country_name)
        LIMIT 1;

        -- Dacă orașul nu există
        IF v_city_id IS NULL THEN
            PERFORM log_action('device', NULL, FORMAT(
                'Attempted to get online count for unknown city: %s > %s > %s',
                p_country_name, p_county_name, p_city_name
            ), p_source_ip);
            RETURN 0;
        END IF;

        -- Numărăm device-urile online
        SELECT COUNT(*)
        INTO v_online_count
        FROM Devices d
        JOIN Nodes n ON d.node_id = n.ID
        WHERE n.city_id = v_city_id
        AND d.status = 'online';

        -- Logăm cererea reușită
        PERFORM log_action('device', NULL, FORMAT(
            'Fetched online device count for city %s > %s > %s = %s',
            p_country_name, p_county_name, p_city_name, v_online_count
        ), p_source_ip);

        -- Returnăm doar numărul
        RETURN v_online_count;
    END;
    $$ LANGUAGE plpgsql;

