--PostgreSQL Maestro 13.7.0.3
------------------------------------------
--Host     : localhost
--Database : dialogs


SET SESSION AUTHORIZATION 'oski';
SET search_path = public, pg_catalog;
ALTER TABLE ONLY public.pullrequest DROP CONSTRAINT foreign_key_pullrequest;
ALTER TABLE ONLY public.pullrequest_comment DROP CONSTRAINT pullrequest_comment_index_fk1;
ALTER TABLE ONLY public.pullrequest DROP CONSTRAINT pullrequest_pkey;
DROP TABLE public."commit";
DROP TABLE public.pullrequest_comment;
DROP TABLE public.pullrequest;
-- Structure for table pullrequest (OID = 40969):
CREATE TABLE pullrequest (
    id integer NOT NULL,
    body text,
    title text,
    repo_owner varchar(32),
    repo_name varchar(64),
    pull_id smallint,
    url text,
    author varchar(32)
) WITHOUT OIDS;
-- Structure for table pullrequest_comment (OID = 40977):
CREATE TABLE pullrequest_comment (
    id smallint,
    author varchar(32),
    body text,
    pullrequest_id integer NOT NULL,
    url text
) WITHOUT OIDS;
-- Structure for table commit (OID = 40990):
CREATE TABLE "commit" (
    sha text,
    author varchar(32)
) WITHOUT OIDS;
-- Definition for index pullrequest_pkey (OID = 40975):
ALTER TABLE ONLY pullrequest
    ADD CONSTRAINT pullrequest_pkey PRIMARY KEY (id);
-- Definition for index pullrequest_comment_index_fk1 (OID = 40983):
ALTER TABLE ONLY pullrequest_comment
    ADD CONSTRAINT pullrequest_comment_index_fk1 UNIQUE (pullrequest_id);
-- Definition for index foreign_key_pullrequest (OID = 40985):
ALTER TABLE ONLY pullrequest
    ADD CONSTRAINT foreign_key_pullrequest FOREIGN KEY (id) REFERENCES pullrequest_comment(pullrequest_id) ON UPDATE CASCADE;
COMMENT ON SCHEMA public IS 'standard public schema';
