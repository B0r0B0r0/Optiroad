CREATE TABLE Countries (
    ID SERIAL PRIMARY KEY,
    country_name VARCHAR NOT NULL,
    country_code VARCHAR UNIQUE NOT NULL
);

CREATE TABLE Counties (
    ID SERIAL PRIMARY KEY,
    county_name VARCHAR NOT NULL,
    country_id INT NOT NULL REFERENCES Countries(ID)
);

CREATE TABLE Cities (
    ID SERIAL PRIMARY KEY,
    city_name VARCHAR NOT NULL,
    county_id INT NOT NULL REFERENCES Counties(ID),
    lat DECIMAL NOT NULL,
    lon DECIMAL NOT NULL
);

CREATE TABLE Users (
    ID SERIAL PRIMARY KEY,
    first_name VARCHAR NOT NULL,
    last_name VARCHAR NOT NULL,
    username VARCHAR UNIQUE NOT NULL,
    password VARCHAR NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    role VARCHAR NOT NULL,
    date_of_birth DATE NOT NULL,
    address VARCHAR NOT NULL,
    profession VARCHAR NOT NULL,
    workplace VARCHAR NOT NULL,
    phone VARCHAR NOT NULL,
    id_front VARCHAR NOT NULL,
    id_back VARCHAR NOT NULL,
    created_at TIMESTAMP NOT NULL,
    approved_at TIMESTAMP,
    status VARCHAR CHECK (status IN ('pending', 'approved', 'rejected'))
);

CREATE TABLE Keys (
    ID SERIAL PRIMARY KEY,
    key VARCHAR UNIQUE NOT NULL,
    created_by INT NOT NULL REFERENCES Users(ID),
    created_at TIMESTAMP NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    expires_at TIMESTAMP
);

ALTER TABLE Users
ADD COLUMN key_id INT;

ALTER TABLE Users
ADD CONSTRAINT fk_user_key
FOREIGN KEY (key_id) REFERENCES Keys(ID);

CREATE TABLE CityManagers (
    ID SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES Users(ID),
    city_id INT NOT NULL REFERENCES Cities(ID),
    start_date DATE NOT NULL,
    end_date DATE
);

CREATE TABLE Logs (
    ID SERIAL PRIMARY KEY,
    action_type VARCHAR CHECK (action_type IN ('login', 'registration', 'key generation', 'cities', 'etc', 'device')),
    user_id INT REFERENCES Users(ID),
    message VARCHAR NOT NULL,
    time_stamp TIMESTAMP NOT NULL,
    source_ip VARCHAR NOT NULL
);

CREATE TABLE Nodes (
    ID SERIAL PRIMARY KEY,
    node_name VARCHAR NOT NULL,
    city_id INT NOT NULL REFERENCES Cities(ID)
);


CREATE TABLE Devices (
    ID SERIAL PRIMARY KEY,
    lat DECIMAL NOT NULL,
    lon DECIMAL NOT NULL,
    ip_address VARCHAR,
    status VARCHAR CHECK (status IN ('online', 'offline')),
    node_id INT NOT NULL REFERENCES Nodes(ID)
);

CREATE TABLE UserApprovals (
    ID SERIAL PRIMARY KEY,
    action_type VARCHAR CHECK (action_type IN ('approved', 'rejected')),
    performed_by INT NOT NULL REFERENCES Users(ID),
    performed_for INT REFERENCES Users(ID),
    user_first_name VARCHAR NOT NULL,
    user_last_name VARCHAR NOT NULL,
    time_stamp TIMESTAMP NOT NULL
);

CREATE TABLE RefreshTokens (
    ID SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES Users(ID),
    token_hash TEXT,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL
);
