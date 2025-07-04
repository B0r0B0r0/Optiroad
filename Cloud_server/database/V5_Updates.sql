CREATE OR REPLACE FUNCTION update_user_password (
    p_username VARCHAR,
    p_new_password VARCHAR,
    p_source_ip VARCHAR
    )
    RETURNS TEXT AS $$
    DECLARE
        v_user_id INT;
    BEGIN
        -- Găsim utilizatorul
        SELECT id INTO v_user_id FROM Users WHERE username = p_username;

        -- Dacă nu există
        IF v_user_id IS NULL THEN
            PERFORM log_action('etc', NULL, FORMAT('Password update failed: user %s not found', p_username), p_source_ip);
            RETURN 'User not found';
        END IF;

        -- Actualizăm parola
        UPDATE Users
        SET password = p_new_password
        WHERE id = v_user_id;

        -- Logăm acțiunea
        PERFORM log_action('etc', v_user_id, FORMAT('Password updated for user %s', p_username), p_source_ip);

        RETURN 'Password updated successfully';
    END;
    $$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION register_user (
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
        v_expires_at TIMESTAMP;
        v_conflict_id INT;
    BEGIN
        -- Verific dacă cheia există și nu a fost folosită
        SELECT ID INTO v_key_id FROM Keys WHERE key = p_registration_key AND is_used = FALSE AND expires_at > NOW();

        IF v_key_id IS NULL THEN
            PERFORM log_action('registration', NULL, FORMAT('Attempted registration with invalid or used key: %s', p_registration_key), p_source_ip);
            RETURN 'Invalid or already used registration key';
        END IF;

        -- Găsesc utilizatorul corespunzător acestei chei
        SELECT ID INTO v_user_id FROM Users WHERE key_id = v_key_id;
        IF v_user_id IS NULL THEN
            PERFORM log_action('registration', NULL, FORMAT('Registration key %s is not linked to any user', p_registration_key), p_source_ip);
            RETURN 'Registration key not linked to a user';
        END IF;

        -- Verificăm dacă username-ul este folosit de altcineva
        SELECT ID INTO v_conflict_id FROM Users WHERE username = p_username AND ID <> v_user_id;
        IF v_conflict_id IS NOT NULL THEN
            PERFORM log_action('registration', v_user_id, FORMAT('Conflict: Username %s already exists', p_username), p_source_ip);
            RETURN 'Username already exists';
        END IF;

        -- Verificăm dacă email-ul este folosit de altcineva
        SELECT ID INTO v_conflict_id FROM Users WHERE email = p_email AND ID <> v_user_id;
        IF v_conflict_id IS NOT NULL AND v_conflict_id <> v_user_id THEN
            PERFORM log_action('registration', v_user_id, FORMAT('Conflict: Email %s already exists', p_email), p_source_ip);
            RETURN 'Email already exists';
        END IF;

        -- Update user
        UPDATE Users
        SET username = p_username,
            password = p_password,
            email = p_email,
            role = 'maintainer'
        WHERE ID = v_user_id;

        -- Marcare cheie ca folosită
        UPDATE Keys
        SET is_used = TRUE
        WHERE ID = v_key_id;

        -- Log
        PERFORM log_action('registration', v_user_id, FORMAT('User %s completed registration', p_username), p_source_ip);

        RETURN 'User registered successfully';
    END;
    $$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION approve_pending_user (
    p_user_id INT,
    p_admin_username VARCHAR,
    p_first_name VARCHAR,
    p_last_name VARCHAR,
    p_source_ip VARCHAR
    )
    RETURNS TEXT AS $$
    DECLARE
        v_admin_id INT;
        v_admin_role VARCHAR;
        v_user_status VARCHAR;
    BEGIN
        -- Verificăm dacă adminul există și este într-adevăr admin
        SELECT ID, role INTO v_admin_id, v_admin_role
        FROM Users
        WHERE username = p_admin_username;

        IF v_admin_id IS NULL THEN
            PERFORM log_action('registration', NULL, FORMAT('Approval failed: invalid admin username %s', p_admin_username), p_source_ip);
            RETURN 'Invalid admin username';
        END IF;

        IF v_admin_role <> 'admin' THEN
            PERFORM log_action('registration', v_admin_id, FORMAT('Approval failed: %s is not admin', p_admin_username), p_source_ip);
            RETURN 'User is not admin';
        END IF;

        -- Verificăm dacă utilizatorul care trebuie aprobat există și este pending
        SELECT status INTO v_user_status
        FROM Users
        WHERE ID = p_user_id;

        IF v_user_status IS DISTINCT FROM 'pending' THEN
            PERFORM log_action('registration', v_admin_id, FORMAT('Approval failed: user ID %s is not pending', p_user_id), p_source_ip);
            RETURN 'User is not pending';
        END IF;

        -- Actualizăm statusul userului
        UPDATE Users
        SET status = 'approved'
        , approved_at = NOW()
        WHERE ID = p_user_id;

        -- Adăugăm intrare în tabela UserApprovals
        INSERT INTO UserApprovals (
            action_type,
            performed_by,
            performed_for,
            user_first_name,
            user_last_name,
            time_stamp
        ) VALUES (
            'approved',
            v_admin_id,
            p_user_id,
            p_first_name,
            p_last_name,
            NOW()
        );

        -- Log de succes
        PERFORM log_action('registration', v_admin_id, FORMAT('User ID %s approved by %s', p_user_id, p_admin_username), p_source_ip);

        RETURN 'User approved successfully';
    END;
    $$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION update_device_status(
    p_device_id INT,
    p_new_status VARCHAR,
    p_source_ip VARCHAR
    )
    RETURNS TEXT AS $$
    DECLARE
        v_exists INT;
    BEGIN
        -- Verificăm dacă statusul este valid
        IF p_new_status NOT IN ('online', 'offline') THEN
            PERFORM log_action('device', NULL, FORMAT(
                'Attempted to set invalid status %s for device ID %s',
                p_new_status, p_device_id
            ), p_source_ip);
            RETURN 'Invalid status value';
        END IF;

        -- Verificăm dacă device-ul există
        SELECT COUNT(*) INTO v_exists
        FROM Devices
        WHERE ID = p_device_id;

        IF v_exists = 0 THEN
            PERFORM log_action('device', NULL, FORMAT(
                'Attempted to update non-existent device ID %s',
                p_device_id
            ), p_source_ip);
            RETURN 'Device not found';
        END IF;

        -- Facem update-ul
        UPDATE Devices
        SET status = p_new_status
        WHERE ID = p_device_id;

        -- Logăm acțiunea
        PERFORM log_action('device', NULL, FORMAT(
            'Device ID %s status updated to %s',
            p_device_id, p_new_status
        ), p_source_ip);

        RETURN 'Device status updated successfully';
    END;
    $$ LANGUAGE plpgsql;
