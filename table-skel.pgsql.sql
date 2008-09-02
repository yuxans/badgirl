--
-- Selected TOC Entries:
--
--
-- TOC Entry ID 12 (OID 18720)
--
-- Name: "plpgsql_call_handler" () Type: FUNCTION Owner: postgres
--

CREATE FUNCTION "plpgsql_call_handler" () RETURNS opaque AS '/usr/lib/postgresql/lib/plpgsql.so', 'plpgsql_call_handler' LANGUAGE 'C';

--
-- TOC Entry ID 13 (OID 18721)
--
-- Name: plpgsql Type: PROCEDURAL LANGUAGE Owner: 
--

CREATE TRUSTED PROCEDURAL LANGUAGE 'plpgsql' HANDLER "plpgsql_call_handler" LANCOMPILER 'PL/pgSQL';

--
-- TOC Entry ID 3 (OID 18725)
--
-- Name: grants Type: TABLE Owner: bradmont
--

CREATE TABLE "grants" (
	"hostmask" character varying(100) NOT NULL,
	"priv_type" character varying(20) NOT NULL,
	Constraint "grants_pkey" Primary Key ("hostmask", "priv_type")
);

--
-- TOC Entry ID 4 (OID 18783)
--
-- Name: data Type: TABLE Owner: bradmont
--

CREATE TABLE "data" (
	"data" character varying(128) NOT NULL,
	"type" character varying(20) NOT NULL,
	"created_by" character varying(100),
	Constraint "data_pkey" Primary Key ("data", "type")
);

--
-- TOC Entry ID 2 (OID 18852)
--
-- Name: poll_sequence Type: SEQUENCE Owner: bradmont
--

CREATE SEQUENCE "poll_sequence" start 1 increment 1 maxvalue 99999999 minvalue 1  cache 1 ;

--
-- TOC Entry ID 5 (OID 18871)
--
-- Name: poll Type: TABLE Owner: bradmont
--

CREATE TABLE "poll" (
	"question" text NOT NULL,
	"poll_num" integer DEFAULT nextval('poll_sequence'::text) NOT NULL,
	Constraint "poll_pkey" Primary Key ("poll_num")
);

--
-- TOC Entry ID 6 (OID 18901)
--
-- Name: poll_options Type: TABLE Owner: bradmont
--

CREATE TABLE "poll_options" (
	"poll_num" integer NOT NULL,
	"option_key" character varying(20) NOT NULL,
	"option_text" character varying(80),
	Constraint "poll_options_pkey" Primary Key ("poll_num", "option_key")
);

--
-- TOC Entry ID 7 (OID 18922)
--
-- Name: poll_votes Type: TABLE Owner: bradmont
--

CREATE TABLE "poll_votes" (
	"voter_nickmask" character varying(128) NOT NULL,
	"option_key" character varying(20) NOT NULL,
	"poll_num" integer NOT NULL,
	Constraint "poll_votes_pkey" Primary Key ("voter_nickmask", "option_key", "poll_num")
);

--
-- TOC Entry ID 8 (OID 18949)
--
-- Name: stats Type: TABLE Owner: bradmont
--

CREATE TABLE "stats" (
	"nick" character varying(31) NOT NULL,
	"type" character varying(20) NOT NULL,
	"counter" double precision,
	Constraint "stats_pkey" Primary Key ("nick", "type")
);

--
-- TOC Entry ID 9 (OID 19574)
--
-- Name: factoids Type: TABLE Owner: bradmont
--

CREATE TABLE "factoids" (
	"factoid_key" character varying(64) NOT NULL,
	"requested_by" character varying(150),
	"requested_time" numeric(11,0),
	"requested_count" integer,
	"created_by" character varying(150),
	"created_time" numeric(11,0),
	"modified_by" character varying(192),
	"modified_time" numeric(11,0),
	"locked_by" character varying(150),
	"locked_time" numeric(11,0),
	"factoid_value" text,
	Constraint "factoids_pkey" Primary Key ("factoid_key")
);

CREATE TABLE IF NOT EXISTS "factoidlink" (
	"linkfrom" character varying(64) NOT NULL,
	"linkto" character varying(64) NOT NULL,
	"linktype" character varying(64) NOT NULL,
	"created_by" character varying(150) NOT NULL,
	"created_time" numeric(11,0) NOT NULL,
	"weight" numeric(4,0) NOT NULL,
	Constraint "factoidlink_pkey" Primary Key("linkfrom","linkto"),
);
CREATE INDEX "linkto" ON "factoidlink" KEY ("linkto");
CREATE INDEX "linktype" ON "factoidlink" KEY ("linktype");

--
-- Name: seentype Type: TABLE Owner: bradmont
--

CREATE TABLE "seentype" (
        "type" character varying(20) NOT NULL,
        Constraint "seentype_pkey" Primary Key ("type")
);

--
-- TOC Entry ID 10 (OID 48376)
--
-- Name: seen Type: TABLE Owner: bradmont
--

CREATE TABLE "seen" (
	"nick" character varying(31) NOT NULL,
	"hostmask" character varying(150),
	"time" numeric(11,0),
	"message" text,
	"type" character varying(20) NOT NULL,
	Constraint "seen_pkey" Primary Key ("nick")
);

--
-- TOC Entry ID 11 (OID 171490)
--
-- Name: webstats Type: TABLE Owner: bradmont
--

CREATE TABLE "webstats" (
	"nick" character varying(255) NOT NULL,
	"count" numeric(10,0) NOT NULL,
	"quote" text,
	"quote_time" numeric(11,0),
	"channel" character varying(255),
	"type" character varying(30) default 'privmsg'
);

--
-- Name: aliastype Type: TABLE Owner: bradmont
--

CREATE TABLE "aliastype" (
        "type" character varying(20) NOT NULL,
        Constraint "aliastype_pkey" Primary Key ("type")
);

--
-- Name: alias Type: TABLE Owner: bradmont
--

CREATE TABLE "alias" (
        "nick" character varying(31) NOT NULL,
        "realnick" character varying(31) NOT NULL,
        "type" character varying(20) NOT NULL
);
CREATE UNIQUE INDEX alias_nick_key ON alias USING btree (nick);

--
-- Name: aliasregex Type: TABLE Owner: bradmont
--

CREATE TABLE "aliasregex" (
        "regex" character varying(64) NOT NULL,
        "realnick" character varying(31) NOT NULL
);
CREATE UNIQUE INDEX aliasregex_regex_key ON aliasregex USING btree (regex);

--
-- Name: urls Type: TABLE Owner: bradmont
--

CREATE TABLE "url" (
	"nick" character varying(64) NOT NULL,
	"time" timestamp NOT NULL,
	"string" text NOT NULL,
	"url_id" serial
);

--
-- TOC Entry ID 18 (OID 18917)
--
-- Name: "RI_ConstraintTrigger_18916" Type: TRIGGER Owner: bradmont
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER INSERT OR UPDATE ON "poll_options"  FROM "poll" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_check_ins" ('<unnamed>', 'poll_options', 'poll', 'UNSPECIFIED', 'poll_num', 'poll_num');

--
-- TOC Entry ID 14 (OID 18919)
--
-- Name: "RI_ConstraintTrigger_18918" Type: TRIGGER Owner: bradmont
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "poll"  FROM "poll_options" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'poll_options', 'poll', 'UNSPECIFIED', 'poll_num', 'poll_num');

--
-- TOC Entry ID 15 (OID 18921)
--
-- Name: "RI_ConstraintTrigger_18920" Type: TRIGGER Owner: bradmont
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "poll"  FROM "poll_options" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'poll_options', 'poll', 'UNSPECIFIED', 'poll_num', 'poll_num');

--
-- TOC Entry ID 21 (OID 18938)
--
-- Name: "RI_ConstraintTrigger_18937" Type: TRIGGER Owner: bradmont
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER INSERT OR UPDATE ON "poll_votes"  FROM "poll_options" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_check_ins" ('<unnamed>', 'poll_votes', 'poll_options', 'UNSPECIFIED', 'option_key', 'option_key', 'poll_num', 'poll_num');

--
-- TOC Entry ID 19 (OID 18940)
--
-- Name: "RI_ConstraintTrigger_18939" Type: TRIGGER Owner: bradmont
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "poll_options"  FROM "poll_votes" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'poll_votes', 'poll_options', 'UNSPECIFIED', 'option_key', 'option_key', 'poll_num', 'poll_num');

--
-- TOC Entry ID 20 (OID 18942)
--
-- Name: "RI_ConstraintTrigger_18941" Type: TRIGGER Owner: bradmont
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "poll_options"  FROM "poll_votes" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'poll_votes', 'poll_options', 'UNSPECIFIED', 'option_key', 'option_key', 'poll_num', 'poll_num');

--
-- TOC Entry ID 22 (OID 18944)
--
-- Name: "RI_ConstraintTrigger_18943" Type: TRIGGER Owner: bradmont
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER INSERT OR UPDATE ON "poll_votes"  FROM "poll" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_check_ins" ('<unnamed>', 'poll_votes', 'poll', 'UNSPECIFIED', 'poll_num', 'poll_num');

--
-- TOC Entry ID 16 (OID 18946)
--
-- Name: "RI_ConstraintTrigger_18945" Type: TRIGGER Owner: bradmont
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "poll"  FROM "poll_votes" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'poll_votes', 'poll', 'UNSPECIFIED', 'poll_num', 'poll_num');

--
-- TOC Entry ID 17 (OID 18948)
--
-- Name: "RI_ConstraintTrigger_18947" Type: TRIGGER Owner: bradmont
--

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "poll"  FROM "poll_votes" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'poll_votes', 'poll', 'UNSPECIFIED', 'poll_num', 'poll_num');


CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER INSERT OR UPDATE ON "alias"  FROM "aliastype" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_check_ins" ('<unnamed>', 'alias', 'aliastype', 'UNSPECIFIED', 'type', 'type');

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "aliastype"  FROM "alias" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'alias', 'aliastype', 'UNSPECIFIED', 'type', 'type');

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "aliastype"  FROM "alias" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'alias', 'aliastype', 'UNSPECIFIED', 'type', 'type');


CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER INSERT OR UPDATE ON "seen"  FROM "seentype" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_check_ins" ('<unnamed>', 'seen', 'seentype', 'UNSPECIFIED', 'type', 'type');

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER DELETE ON "seentype"  FROM "seen" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_del" ('<unnamed>', 'seen', 'seentype', 'UNSPECIFIED', 'type', 'type');

CREATE CONSTRAINT TRIGGER "<unnamed>" AFTER UPDATE ON "seentype"  FROM "seen" NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE "RI_FKey_noaction_upd" ('<unnamed>', 'seen', 'seentype', 'UNSPECIFIED', 'type', 'type');


COPY "aliastype" FROM stdin;
regex
nickchange
confirmed
cached
\.

COPY "seentype" FROM stdin;
privmsg
action
nick
join
part
quit
\.
