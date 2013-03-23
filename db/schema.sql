DROP DATABASE IF EXISTS simalytics;

DROP USER simalytics@localhost;

CREATE DATABASE simalytics;

USE simalytics;

-- Users
CREATE TABLE T_USER (
       ID INTEGER AUTO_INCREMENT,
       EMAIL_ADDRESS VARCHAR(100),
       FIRST_NAME VARCHAR(100),
       SURNAME VARCHAR(100),
       CREATED DATETIME,
       LAST_LOGIN DATETIME,
       TOS_ACCEPTANCE BOOLEAN,
       PASSWORD_HASH VARCHAR(100),
       SOURCE VARCHAR(100), -- Facebook/OpenID
       STATUS_ID INTEGER,
       PRIMARY KEY (ID)
);

CREATE TABLE T_USER_STATUS (
       ID INTEGER,
       CODE VARCHAR(20),
       DESCRIPTION VARCHAR(255),
       PRIMARY KEY (ID)
);

ALTER TABLE T_USER ADD CONSTRAINT T_USER_FK1 FOREIGN KEY (STATUS_ID) REFERENCES T_USER_STATUS (ID);

-- Profiles
CREATE TABLE T_PROFILE (
       ID INTEGER AUTO_INCREMENT,
       USER_ID INTEGER,
       TITLE VARCHAR(200), -- Drawn from site home page via HTTP request
       URL VARCHAR(100),
       PRIVATE_KEY BLOB, -- for session verification
       CREATED DATETIME,
       DELETED DATETIME,
       STATUS_ID INTEGER,
       PRIMARY KEY (ID)
);

-- ALTER TABLE T_PROFILE ADD CONSTRAINT T_PROFILE_FK1 FOREIGN KEY (USER_ID) REFERENCES T_USER(ID);
-- ALTER TABLE T_PROFILE ADD CONSTRAINT T_PROFILE_FK1 FOREIGN KEY (USER_ID) REFERENCES visitor_visitor (id);

CREATE TABLE T_PROFILE_STATUS (
       ID INTEGER,
       CODE VARCHAR(20),
       DESCRIPTION VARCHAR(255),
       PRIMARY KEY (ID)
);

ALTER TABLE T_PROFILE ADD CONSTRAINT T_PROFILE_FK2 FOREIGN KEY (STATUS_ID) REFERENCES T_PROFILE_STATUS (ID);

-- Sessions
CREATE TABLE T_GUEST_SESSION (
       START_TIME DATETIME,
       DURATION_MS LONG,
       PROFILE_ID INTEGER,
       SOURCE_IP VARCHAR(20),
       EXTERN_IDENT VARCHAR(100), -- hashed external identifier
       PRIMARY KEY (EXTERN_IDENT)
);

ALTER TABLE T_GUEST_SESSION ADD CONSTRAINT T_GUEST_SESSION_FK1 FOREIGN KEY (PROFILE_ID) REFERENCES T_PROFILE (ID);

-- PCUs
CREATE TABLE T_PCU (
       ID INTEGER AUTO_INCREMENT,
       PROFILE_ID INTEGER,
       PUBLIC_KEY BLOB, -- for session generation
       URL VARCHAR(255),
       PCU_IDENTIFIER VARCHAR(255), -- dependent on the client, may be a single identifier (forum thread ID, or multiple, e.g. "<thread-ID>;<post-ID>"
       CREATED DATETIME,
       MODIFIED DATETIME,
       STATUS_ID INTEGER,
       PRIMARY KEY (ID)
);

-- PCU mapped back to user (creator) via T_PROFILE
ALTER TABLE T_PCU ADD CONSTRAINT T_PCU_FK1 FOREIGN KEY (PROFILE_ID) REFERENCES T_PROFILE (ID);

CREATE TABLE T_PCU_STATUS (
       ID INTEGER,
       CODE VARCHAR(20),
       DESCRIPTION VARCHAR(255),
       PRIMARY KEY (ID)
);

ALTER TABLE T_PCU ADD CONSTRAINT T_PCU_FK2 FOREIGN KEY (STATUS_ID) REFERENCES T_PCU_STATUS (ID);

-- Interactions
CREATE TABLE T_PCU_INTERACTION (
       ID INTEGER AUTO_INCREMENT,
       PCU_ID INTEGER,
       INTERACTION_TIME DATETIME,
       ACTION_ID INTEGER, -- OVERLAY_OPENED, MORE_INFORMATION, CANCEL, PAY ... use enum?
       SESSION_IDENT VARCHAR(100),
       PRIMARY KEY (ID)
);

ALTER TABLE T_PCU_INTERACTION ADD CONSTRAINT T_PCU_INTERACTION_FK1 FOREIGN KEY (PCU_ID) REFERENCES T_PCU (ID);
ALTER TABLE T_PCU_INTERACTION ADD CONSTRAINT T_PCU_INTERACTION_FK2 FOREIGN KEY (SESSION_IDENT) REFERENCES T_GUEST_SESSION (EXTERN_IDENT);

CREATE TABLE T_PCU_INTERACTION_ACTION (
       ID INTEGER AUTO_INCREMENT,
       CODE VARCHAR(20),
       DESCRIPTION VARCHAR(255),
       PRIMARY KEY (ID)
);

ALTER TABLE T_PCU_INTERACTION ADD CONSTRAINT T_PCU_INTERACTION_FK3 FOREIGN KEY (ACTION_ID) REFERENCES T_PCU_INTERACTION_ACTION (ID);

-- Interaction data
CREATE TABLE T_PCU_INTERACTION_DATA (
       ID INTEGER AUTO_INCREMENT,
       PCU_INTERACTION_ID INTEGER,
       HTTP_HEADERS TEXT,
       PRIMARY KEY (ID)
);

ALTER TABLE T_PCU_INTERACTION_DATA ADD CONSTRAINT T_PCU_INTERACTION_DATA_FK1 FOREIGN KEY (PCU_INTERACTION_ID) REFERENCES T_PCU_INTERACTION (ID);

-- Analytics data
CREATE TABLE T_PROFILE_ANALYTICS (
       PROFILE_ID INTEGER,
       HOUR DATETIME, -- Date/hour
       OVERLAY_OPEN_CLICKS INTEGER,
       ACCEPT_CLICKS INTEGER,
       MORE_INFORMATION_CLICKS INTEGER,
       DECLINE_CLICKS INTEGER,
       PRIMARY KEY (PROFILE_ID, HOUR)
);

ALTER TABLE T_PROFILE_ANALYTICS ADD CONSTRAINT T_PROFILE_ANALYTICS_FK1 FOREIGN KEY (PROFILE_ID) REFERENCES T_PROFILE (ID);

CREATE TABLE T_PCU_ANALYTICS (
       PCU_ID INTEGER,
       HOUR DATETIME, -- Date/hour
       OVERLAY_OPEN_CLICKS INTEGER,
       ACCEPT_CLICKS INTEGER,
       MORE_INFORMATION_CLICKS INTEGER,
       DECLINE_CLICKS INTEGER,
       PRIMARY KEY (PCU_ID, HOUR)
);

ALTER TABLE T_PCU_ANALYTICS ADD CONSTRAINT T_PCU_ANALYTICS_FK1 FOREIGN KEY (PCU_ID) REFERENCES T_PCU (ID);

-- User(s)
GRANT ALL ON simalytics.* TO simalytics@localhost IDENTIFIED BY 's1m@lytic3';

-- Basic data
INSERT INTO T_PROFILE_STATUS (CODE, DESCRIPTION) VALUES ('ACTIVE', 'Default state');
INSERT INTO T_PCU_STATUS (CODE, DESCRIPTION) VALUES ('ACTIVE', 'Default state');

INSERT INTO T_PCU_INTERACTION_ACTION (CODE, DESCRIPTION) VALUES 
       ('OVERLAY_REQUEST', 'Overlay request'),
       ('CLICK_PAY', 'Payment click'),
       ('CLICK_CANCEL', 'Cancellation click'),
       ('CLICK_MORE_INFO', 'More information request')
;