CREATE OR REPLACE FUNCTION revoke_refresh_token (
    p_username VARCHAR,
    p_source_ip VARCHAR
    )
    RETURNS TEXT AS $$
    DECLARE
        v_user_id INT;
        v_refresh_token_id INT;
    BEGIN
        -- Căutăm utilizatorul
        SELECT ID INTO v_user_id
        FROM Users
        WHERE username = p_username;

        IF v_user_id IS NULL THEN
            PERFORM log_action('login', NULL, FORMAT('Attempted to revoke refresh token with invalid username: %s', p_username), p_source_ip);
            RETURN 'Invalid username';
        END IF;

        -- Verificăm dacă are un token activ
        SELECT ID INTO v_refresh_token_id
        FROM refresh_tokens
        WHERE user_id = v_user_id;

        IF v_refresh_token_id IS NULL THEN
            PERFORM log_action('login', v_user_id, FORMAT('Attempted to revoke non-existent refresh token for user: %s', p_username), p_source_ip);
            RETURN 'User does not have a refresh token';
        END IF;

        -- Ștergem tokenul
        DELETE FROM refresh_tokens
        WHERE ID = v_refresh_token_id;

        -- Logare acțiune
        PERFORM log_action('login', v_user_id, FORMAT('Refresh token revoked successfully for user: %s', p_username), p_source_ip);

        RETURN 'Refresh token revoked successfully';
    END;
    $$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION deny_pending_user (
    p_username VARCHAR,
    p_user_id INT,
    p_source_ip VARCHAR
    )
    RETURNS TEXT AS $$
    DECLARE
        v_admin_id INT;
        v_admin_role VARCHAR;
        v_target_status VARCHAR;
        v_first_name VARCHAR;
        v_last_name VARCHAR;
    BEGIN
        -- Verific adminul
        SELECT ID, role INTO v_admin_id, v_admin_role
        FROM Users
        WHERE username = p_username;

        IF v_admin_id IS NULL THEN
            PERFORM log_action('etc', NULL, FORMAT('Attempted to deny pending user with invalid admin username: %s', p_username), p_source_ip);
            RETURN 'Invalid admin username';
        END IF;

        IF v_admin_role != 'admin' THEN
            PERFORM log_action('etc', v_admin_id, FORMAT('Non-admin %s attempted to deny a user', p_username), p_source_ip);
            RETURN 'Permission denied: not an admin';
        END IF;

        -- Verific targetul
        SELECT status, first_name, last_name INTO v_target_status, v_first_name, v_last_name
        FROM Users
        WHERE ID = p_user_id;

        IF v_target_status IS NULL THEN
            PERFORM log_action('etc', v_admin_id, FORMAT('Attempted to deny non-existent user ID: %s', v_admin_id), p_source_ip);
            RETURN 'User not found';
        ELSIF v_target_status != 'pending' THEN
            PERFORM log_action('etc', v_admin_id, FORMAT('Attempted to deny user ID %s which is not pending', v_admin_id), p_source_ip);
            RETURN 'User is not in pending state';
        END IF;

        INSERT INTO UserApprovals (
            action_type,
            performed_by,
            user_first_name,
            user_last_name,
            time_stamp
        ) VALUES (
            'rejected',
            v_admin_id,
            v_first_name,
            v_last_name,
            NOW()
        );

        DELETE FROM Logs WHERE user_id = p_user_id;

        DELETE FROM Users WHERE ID = p_user_id;

        PERFORM log_action('etc', v_admin_id, FORMAT('Admin %s denied and deleted pending user ID %s', p_username, p_user_id), p_source_ip);

        RETURN 'Pending user denied and deleted successfully';
    END;
    $$ LANGUAGE plpgsql;
