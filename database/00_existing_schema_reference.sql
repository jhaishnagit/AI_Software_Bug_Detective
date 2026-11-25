--
-- PostgreSQL database dump
--




SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 231 (class 1259 OID 124806)
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);



--
-- TOC entry 226 (class 1259 OID 124735)
-- Name: bug_analysis; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bug_analysis (
    id integer NOT NULL,
    bug_id integer NOT NULL,
    root_cause text NOT NULL,
    confidence double precision NOT NULL,
    severity character varying(20) NOT NULL,
    affected_component character varying(180) NOT NULL,
    possible_causes text NOT NULL,
    suggested_fix text NOT NULL,
    recommended_actions text NOT NULL,
    provider character varying(40) NOT NULL,
    created_at timestamp with time zone NOT NULL
);



--
-- TOC entry 225 (class 1259 OID 124734)
-- Name: bug_analysis_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.bug_analysis_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- TOC entry 5036 (class 0 OID 0)
-- Dependencies: 225
-- Name: bug_analysis_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.bug_analysis_id_seq OWNED BY public.bug_analysis.id;


--
-- TOC entry 230 (class 1259 OID 124784)
-- Name: bug_attachments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bug_attachments (
    id integer NOT NULL,
    bug_id integer NOT NULL,
    original_name character varying(255) NOT NULL,
    stored_name character varying(255) NOT NULL,
    content_type character varying(120) NOT NULL,
    size_bytes integer NOT NULL,
    extracted_text text NOT NULL,
    created_at timestamp with time zone NOT NULL
);



--
-- TOC entry 229 (class 1259 OID 124783)
-- Name: bug_attachments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.bug_attachments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- TOC entry 5037 (class 0 OID 0)
-- Dependencies: 229
-- Name: bug_attachments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.bug_attachments_id_seq OWNED BY public.bug_attachments.id;


--
-- TOC entry 224 (class 1259 OID 124699)
-- Name: bugs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bugs (
    id integer NOT NULL,
    title character varying(220) NOT NULL,
    description text NOT NULL,
    error_message text NOT NULL,
    reproduction_steps text NOT NULL,
    expected_result text NOT NULL,
    actual_result text NOT NULL,
    module character varying(120) NOT NULL,
    environment character varying(120) NOT NULL,
    severity character varying(20) NOT NULL,
    status character varying(30) NOT NULL,
    project_id integer NOT NULL,
    reporter_id integer NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);



--
-- TOC entry 223 (class 1259 OID 124698)
-- Name: bugs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.bugs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- TOC entry 5038 (class 0 OID 0)
-- Dependencies: 223
-- Name: bugs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.bugs_id_seq OWNED BY public.bugs.id;


--
-- TOC entry 232 (class 1259 OID 132920)
-- Name: project_uploads; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.project_uploads (
    upload_id character varying(32) NOT NULL,
    owner_id integer NOT NULL,
    created_at timestamp with time zone NOT NULL,
    project_id integer
);



--
-- TOC entry 222 (class 1259 OID 124677)
-- Name: projects; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.projects (
    id integer NOT NULL,
    name character varying(180) NOT NULL,
    description text NOT NULL,
    technology character varying(255) NOT NULL,
    repository_url character varying(500) NOT NULL,
    owner_id integer NOT NULL,
    created_at timestamp with time zone NOT NULL
);



--
-- TOC entry 221 (class 1259 OID 124676)
-- Name: projects_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.projects_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- TOC entry 5039 (class 0 OID 0)
-- Dependencies: 221
-- Name: projects_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.projects_id_seq OWNED BY public.projects.id;


--
-- TOC entry 234 (class 1259 OID 132937)
-- Name: source_chunks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.source_chunks (
    id integer NOT NULL,
    upload_id character varying(32) NOT NULL,
    owner_id integer NOT NULL,
    source_name character varying(512) NOT NULL,
    chunk_index integer NOT NULL,
    content text NOT NULL,
    embedding json NOT NULL,
    created_at timestamp with time zone NOT NULL
);



--
-- TOC entry 233 (class 1259 OID 132936)
-- Name: source_chunks_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.source_chunks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- TOC entry 5040 (class 0 OID 0)
-- Dependencies: 233
-- Name: source_chunks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.source_chunks_id_seq OWNED BY public.source_chunks.id;


--
-- TOC entry 228 (class 1259 OID 124761)
-- Name: test_cases; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.test_cases (
    id integer NOT NULL,
    bug_id integer,
    scenario character varying(240) NOT NULL,
    input_data text NOT NULL,
    expected_result text NOT NULL,
    priority character varying(20) NOT NULL,
    test_type character varying(30) NOT NULL,
    executed boolean NOT NULL,
    project_id integer,
    upload_id character varying(32),
    source_key character varying(64)
);



--
-- TOC entry 227 (class 1259 OID 124760)
-- Name: test_cases_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.test_cases_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- TOC entry 5041 (class 0 OID 0)
-- Dependencies: 227
-- Name: test_cases_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.test_cases_id_seq OWNED BY public.test_cases.id;


--
-- TOC entry 236 (class 1259 OID 141129)
-- Name: test_execution_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.test_execution_history (
    id integer NOT NULL,
    upload_id character varying(32) NOT NULL,
    project_id integer,
    test_case_id integer,
    initiated_by integer NOT NULL,
    status character varying(40) NOT NULL,
    execution_mode character varying(40) NOT NULL,
    total integer NOT NULL,
    passed integer NOT NULL,
    failed integer NOT NULL,
    errors integer NOT NULL,
    skipped integer NOT NULL,
    duration_seconds double precision NOT NULL,
    runtime_executed boolean NOT NULL,
    output text NOT NULL,
    error_message text NOT NULL,
    failure_reason text NOT NULL,
    started_at timestamp with time zone NOT NULL,
    completed_at timestamp with time zone NOT NULL
);



--
-- TOC entry 235 (class 1259 OID 141128)
-- Name: test_execution_history_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.test_execution_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- TOC entry 5042 (class 0 OID 0)
-- Dependencies: 235
-- Name: test_execution_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.test_execution_history_id_seq OWNED BY public.test_execution_history.id;


--
-- TOC entry 220 (class 1259 OID 124661)
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    name character varying(120) NOT NULL,
    email character varying(255) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role character varying(30) NOT NULL,
    created_at timestamp with time zone NOT NULL
);



--
-- TOC entry 219 (class 1259 OID 124660)
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- TOC entry 5043 (class 0 OID 0)
-- Dependencies: 219
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- TOC entry 4801 (class 2604 OID 124738)
-- Name: bug_analysis id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bug_analysis ALTER COLUMN id SET DEFAULT nextval('public.bug_analysis_id_seq'::regclass);


--
-- TOC entry 4803 (class 2604 OID 124787)
-- Name: bug_attachments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bug_attachments ALTER COLUMN id SET DEFAULT nextval('public.bug_attachments_id_seq'::regclass);


--
-- TOC entry 4800 (class 2604 OID 124702)
-- Name: bugs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bugs ALTER COLUMN id SET DEFAULT nextval('public.bugs_id_seq'::regclass);


--
-- TOC entry 4799 (class 2604 OID 124680)
-- Name: projects id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.projects ALTER COLUMN id SET DEFAULT nextval('public.projects_id_seq'::regclass);


--
-- TOC entry 4804 (class 2604 OID 132940)
-- Name: source_chunks id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.source_chunks ALTER COLUMN id SET DEFAULT nextval('public.source_chunks_id_seq'::regclass);


--
-- TOC entry 4802 (class 2604 OID 124764)
-- Name: test_cases id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_cases ALTER COLUMN id SET DEFAULT nextval('public.test_cases_id_seq'::regclass);


--
-- TOC entry 4805 (class 2604 OID 141132)
-- Name: test_execution_history id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_execution_history ALTER COLUMN id SET DEFAULT nextval('public.test_execution_history_id_seq'::regclass);


--
-- TOC entry 4798 (class 2604 OID 124664)
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- TOC entry 5025 (class 0 OID 124806)
-- Dependencies: 231
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 5020 (class 0 OID 124735)
-- Dependencies: 226
-- Data for Name: bug_analysis; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 5024 (class 0 OID 124784)
-- Dependencies: 230
-- Data for Name: bug_attachments; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 5018 (class 0 OID 124699)
-- Dependencies: 224
-- Data for Name: bugs; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 5026 (class 0 OID 132920)
-- Dependencies: 232
-- Data for Name: project_uploads; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 5016 (class 0 OID 124677)
-- Dependencies: 222
-- Data for Name: projects; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 5028 (class 0 OID 132937)
-- Dependencies: 234
-- Data for Name: source_chunks; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 5022 (class 0 OID 124761)
-- Dependencies: 228
-- Data for Name: test_cases; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 5030 (class 0 OID 141129)
-- Dependencies: 236
-- Data for Name: test_execution_history; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 5014 (class 0 OID 124661)
-- Dependencies: 220
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 5044 (class 0 OID 0)
-- Dependencies: 225
-- Name: bug_analysis_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.bug_analysis_id_seq', 66, true);


--
-- TOC entry 5045 (class 0 OID 0)
-- Dependencies: 229
-- Name: bug_attachments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.bug_attachments_id_seq', 1, true);


--
-- TOC entry 5046 (class 0 OID 0)
-- Dependencies: 223
-- Name: bugs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.bugs_id_seq', 64, true);


--
-- TOC entry 5047 (class 0 OID 0)
-- Dependencies: 221
-- Name: projects_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.projects_id_seq', 63, true);


--
-- TOC entry 5048 (class 0 OID 0)
-- Dependencies: 233
-- Name: source_chunks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.source_chunks_id_seq', 1, false);


--
-- TOC entry 5049 (class 0 OID 0)
-- Dependencies: 227
-- Name: test_cases_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.test_cases_id_seq', 206, true);


--
-- TOC entry 5050 (class 0 OID 0)
-- Dependencies: 235
-- Name: test_execution_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.test_execution_history_id_seq', 2, true);


--
-- TOC entry 5051 (class 0 OID 0)
-- Dependencies: 219
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 395, true);


--
-- TOC entry 4831 (class 2606 OID 124811)
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- TOC entry 4817 (class 2606 OID 124753)
-- Name: bug_analysis bug_analysis_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bug_analysis
    ADD CONSTRAINT bug_analysis_pkey PRIMARY KEY (id);


--
-- TOC entry 4828 (class 2606 OID 124799)
-- Name: bug_attachments bug_attachments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bug_attachments
    ADD CONSTRAINT bug_attachments_pkey PRIMARY KEY (id);


--
-- TOC entry 4813 (class 2606 OID 124721)
-- Name: bugs bugs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bugs
    ADD CONSTRAINT bugs_pkey PRIMARY KEY (id);


--
-- TOC entry 4835 (class 2606 OID 132927)
-- Name: project_uploads project_uploads_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_uploads
    ADD CONSTRAINT project_uploads_pkey PRIMARY KEY (upload_id);


--
-- TOC entry 4811 (class 2606 OID 124691)
-- Name: projects projects_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (id);


--
-- TOC entry 4840 (class 2606 OID 132952)
-- Name: source_chunks source_chunks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.source_chunks
    ADD CONSTRAINT source_chunks_pkey PRIMARY KEY (id);


--
-- TOC entry 4842 (class 2606 OID 132954)
-- Name: source_chunks source_chunks_upload_id_source_name_chunk_index_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.source_chunks
    ADD CONSTRAINT source_chunks_upload_id_source_name_chunk_index_key UNIQUE (upload_id, source_name, chunk_index);


--
-- TOC entry 4824 (class 2606 OID 124776)
-- Name: test_cases test_cases_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_cases
    ADD CONSTRAINT test_cases_pkey PRIMARY KEY (id);


--
-- TOC entry 4849 (class 2606 OID 141153)
-- Name: test_execution_history test_execution_history_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_execution_history
    ADD CONSTRAINT test_execution_history_pkey PRIMARY KEY (id);


--
-- TOC entry 4826 (class 2606 OID 149337)
-- Name: test_cases uq_test_cases_upload_source_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_cases
    ADD CONSTRAINT uq_test_cases_upload_source_key UNIQUE (upload_id, source_key);


--
-- TOC entry 4808 (class 2606 OID 124674)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 4818 (class 1259 OID 124759)
-- Name: ix_bug_analysis_bug_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bug_analysis_bug_id ON public.bug_analysis USING btree (bug_id);


--
-- TOC entry 4829 (class 1259 OID 124805)
-- Name: ix_bug_attachments_bug_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bug_attachments_bug_id ON public.bug_attachments USING btree (bug_id);


--
-- TOC entry 4814 (class 1259 OID 124733)
-- Name: ix_bugs_project_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bugs_project_id ON public.bugs USING btree (project_id);


--
-- TOC entry 4815 (class 1259 OID 124732)
-- Name: ix_bugs_title; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bugs_title ON public.bugs USING btree (title);


--
-- TOC entry 4832 (class 1259 OID 132933)
-- Name: ix_project_uploads_owner_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_uploads_owner_id ON public.project_uploads USING btree (owner_id);


--
-- TOC entry 4833 (class 1259 OID 149325)
-- Name: ix_project_uploads_project_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_project_uploads_project_id ON public.project_uploads USING btree (project_id);


--
-- TOC entry 4809 (class 1259 OID 124697)
-- Name: ix_projects_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_projects_name ON public.projects USING btree (name);


--
-- TOC entry 4836 (class 1259 OID 132966)
-- Name: ix_source_chunks_owner_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_source_chunks_owner_id ON public.source_chunks USING btree (owner_id);


--
-- TOC entry 4837 (class 1259 OID 132965)
-- Name: ix_source_chunks_owner_upload; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_source_chunks_owner_upload ON public.source_chunks USING btree (owner_id, upload_id);


--
-- TOC entry 4838 (class 1259 OID 132967)
-- Name: ix_source_chunks_upload_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_source_chunks_upload_id ON public.source_chunks USING btree (upload_id);


--
-- TOC entry 4819 (class 1259 OID 124782)
-- Name: ix_test_cases_bug_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_test_cases_bug_id ON public.test_cases USING btree (bug_id);


--
-- TOC entry 4820 (class 1259 OID 149338)
-- Name: ix_test_cases_project_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_test_cases_project_id ON public.test_cases USING btree (project_id);


--
-- TOC entry 4821 (class 1259 OID 149340)
-- Name: ix_test_cases_project_upload; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_test_cases_project_upload ON public.test_cases USING btree (project_id, upload_id);


--
-- TOC entry 4822 (class 1259 OID 149339)
-- Name: ix_test_cases_upload_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_test_cases_upload_id ON public.test_cases USING btree (upload_id);


--
-- TOC entry 4843 (class 1259 OID 141175)
-- Name: ix_test_execution_history_initiated_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_test_execution_history_initiated_by ON public.test_execution_history USING btree (initiated_by);


--
-- TOC entry 4844 (class 1259 OID 141177)
-- Name: ix_test_execution_history_project_created; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_test_execution_history_project_created ON public.test_execution_history USING btree (project_id, started_at);


--
-- TOC entry 4845 (class 1259 OID 141176)
-- Name: ix_test_execution_history_project_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_test_execution_history_project_id ON public.test_execution_history USING btree (project_id);


--
-- TOC entry 4846 (class 1259 OID 141178)
-- Name: ix_test_execution_history_upload_created; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_test_execution_history_upload_created ON public.test_execution_history USING btree (upload_id, started_at);


--
-- TOC entry 4847 (class 1259 OID 141174)
-- Name: ix_test_execution_history_upload_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_test_execution_history_upload_id ON public.test_execution_history USING btree (upload_id);


--
-- TOC entry 4806 (class 1259 OID 124675)
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- TOC entry 4853 (class 2606 OID 124754)
-- Name: bug_analysis bug_analysis_bug_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bug_analysis
    ADD CONSTRAINT bug_analysis_bug_id_fkey FOREIGN KEY (bug_id) REFERENCES public.bugs(id);


--
-- TOC entry 4857 (class 2606 OID 124800)
-- Name: bug_attachments bug_attachments_bug_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bug_attachments
    ADD CONSTRAINT bug_attachments_bug_id_fkey FOREIGN KEY (bug_id) REFERENCES public.bugs(id);


--
-- TOC entry 4851 (class 2606 OID 124722)
-- Name: bugs bugs_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bugs
    ADD CONSTRAINT bugs_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id);


--
-- TOC entry 4852 (class 2606 OID 124727)
-- Name: bugs bugs_reporter_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bugs
    ADD CONSTRAINT bugs_reporter_id_fkey FOREIGN KEY (reporter_id) REFERENCES public.users(id);


--
-- TOC entry 4858 (class 2606 OID 149320)
-- Name: project_uploads fk_project_uploads_project_id_projects; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_uploads
    ADD CONSTRAINT fk_project_uploads_project_id_projects FOREIGN KEY (project_id) REFERENCES public.projects(id);


--
-- TOC entry 4854 (class 2606 OID 149326)
-- Name: test_cases fk_test_cases_project_id_projects; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_cases
    ADD CONSTRAINT fk_test_cases_project_id_projects FOREIGN KEY (project_id) REFERENCES public.projects(id);


--
-- TOC entry 4855 (class 2606 OID 149331)
-- Name: test_cases fk_test_cases_upload_id_project_uploads; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_cases
    ADD CONSTRAINT fk_test_cases_upload_id_project_uploads FOREIGN KEY (upload_id) REFERENCES public.project_uploads(upload_id);


--
-- TOC entry 4859 (class 2606 OID 132928)
-- Name: project_uploads project_uploads_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_uploads
    ADD CONSTRAINT project_uploads_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(id);


--
-- TOC entry 4850 (class 2606 OID 124692)
-- Name: projects projects_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(id);


--
-- TOC entry 4860 (class 2606 OID 132960)
-- Name: source_chunks source_chunks_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.source_chunks
    ADD CONSTRAINT source_chunks_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(id);


--
-- TOC entry 4861 (class 2606 OID 132955)
-- Name: source_chunks source_chunks_upload_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.source_chunks
    ADD CONSTRAINT source_chunks_upload_id_fkey FOREIGN KEY (upload_id) REFERENCES public.project_uploads(upload_id);


--
-- TOC entry 4856 (class 2606 OID 124777)
-- Name: test_cases test_cases_bug_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_cases
    ADD CONSTRAINT test_cases_bug_id_fkey FOREIGN KEY (bug_id) REFERENCES public.bugs(id);


--
-- TOC entry 4862 (class 2606 OID 141169)
-- Name: test_execution_history test_execution_history_initiated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_execution_history
    ADD CONSTRAINT test_execution_history_initiated_by_fkey FOREIGN KEY (initiated_by) REFERENCES public.users(id);


--
-- TOC entry 4863 (class 2606 OID 141159)
-- Name: test_execution_history test_execution_history_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_execution_history
    ADD CONSTRAINT test_execution_history_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id);


--
-- TOC entry 4864 (class 2606 OID 141164)
-- Name: test_execution_history test_execution_history_test_case_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_execution_history
    ADD CONSTRAINT test_execution_history_test_case_id_fkey FOREIGN KEY (test_case_id) REFERENCES public.test_cases(id);


--
-- TOC entry 4865 (class 2606 OID 141154)
-- Name: test_execution_history test_execution_history_upload_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_execution_history
    ADD CONSTRAINT test_execution_history_upload_id_fkey FOREIGN KEY (upload_id) REFERENCES public.project_uploads(upload_id);



--
-- PostgreSQL database dump complete
--
