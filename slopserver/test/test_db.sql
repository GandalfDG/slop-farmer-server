PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE domain (
	id INTEGER NOT NULL, 
	domain_name VARCHAR NOT NULL, 
	CONSTRAINT pk_domain PRIMARY KEY (id)
);
INSERT INTO domain VALUES(1,'google.com');
INSERT INTO domain VALUES(2,'moogle.com');
CREATE TABLE user (
	id INTEGER NOT NULL, 
	email VARCHAR NOT NULL, 
	password_hash VARCHAR NOT NULL, 
	email_verified BOOLEAN NOT NULL, 
	CONSTRAINT pk_user PRIMARY KEY (id)
);
INSERT INTO user VALUES(1,'alphauser01','$argon2id$v=19$m=65536,t=3,p=4$3z7uxa3NHl/dKG07RGEvBA$0NOBftJpP+HiR7wfgdwBk2UR9F12YBjrqeqLSyDl47o','True');
CREATE TABLE path (
	id INTEGER NOT NULL, 
	path VARCHAR NOT NULL, 
	domain_id INTEGER, 
	CONSTRAINT pk_path PRIMARY KEY (id), 
	CONSTRAINT fk_path_domain_id_domain FOREIGN KEY(domain_id) REFERENCES domain (id)
);
INSERT INTO path VALUES(1,'/',0);
INSERT INTO path VALUES(2,'/path1',0);
INSERT INTO path VALUES(3,'/path2',1);
INSERT INTO path VALUES(4,'/path3/a',1);
INSERT INTO path VALUES(5,'/path4',1);
INSERT INTO path VALUES(6,'/path2',2);
INSERT INTO path VALUES(7,'/',2);
INSERT INTO path VALUES(8,'/path3',2);
INSERT INTO path VALUES(9,'/path4',2);
CREATE TABLE report (
	path_id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	timestamp DATETIME, 
	CONSTRAINT pk_report PRIMARY KEY (path_id, user_id), 
	CONSTRAINT fk_report_path_id_path FOREIGN KEY(path_id) REFERENCES path (id), 
	CONSTRAINT fk_report_user_id_user FOREIGN KEY(user_id) REFERENCES user (id)
);
INSERT INTO report VALUES(2,1,'11-26-2025');
CREATE UNIQUE INDEX ix_domain_domain_name ON domain (domain_name);
CREATE UNIQUE INDEX ix_user_email ON user (email);
COMMIT;
