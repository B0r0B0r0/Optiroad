--INSERT INTO Users(username, password, email, role) VALUES ('admin', 'admin', 'admin@admin.com','admin');
--select add_key('1111-1111-1111-1111','admin','1.1.1.1');
--select add_key('1111-1111-1111-1112','admin','1.1.1.1');

INSERT INTO Users(first_name,last_name, username, password, email, role, date_of_birth, address, profession, workplace, phone, id_front, id_back, created_at, status)
VALUES ('Admin', 'Admin', 'admin', 'JDJiJDEyJEIyT2plOWpiU08wNjZpWkdza0l3aWU1YnVSU1Y3U2E3c2ttQjlYTEtvWHpsWG5zRzBZYkF1', 'admin@admin.com', 'admin', '1990-01-01', '123 Admin St', 'Administrator', 'Admin Corp', '123-456-7890', 'id_front.jpg', 'id_back.jpg', NOW(), 'approved');