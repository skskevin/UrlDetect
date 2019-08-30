# Coefficient used for a time-based query delay checking (must be >= 7)
TIME_STDEV_COEFF = 2
# Minimum time response set needed for time-comparison based on standard deviation
MIN_TIME_RESPONSES = 30
# Maximum time response set used during time-comparison based on standard deviation
MAX_TIME_RESPONSES = 200
# Minimum response time that can be even considered as delayed (not a complete requirement)
MIN_VALID_DELAYED_RESPONSE = 0.5

# Step used in ORDER BY technique used for finding the right number of columns in UNION query injections
ORDER_BY_STEP = 10
# Minimum length of usable union injected response (quick defense against substr fields)
UNION_MIN_RESPONSE_CHARS = 10

# Coefficient used for a union-based number of columns checking (must be >= 7)
UNION_STDEV_COEFF = 7

# Character used as a boundary in kb.chars (preferably less frequent letter)
KB_CHARS_BOUNDARY_CHAR = 'q'

# Letters of lower frequency used in kb.chars
KB_CHARS_LOW_FREQUENCY_ALPHABET = "zqxjkvbp"

# Mark used for replacement of reflected values
REFLECTED_VALUE_MARKER = "__REFLECTED_VALUE__"

# Regular expression used for replacing border non-alphanum characters
REFLECTED_BORDER_REGEX = r"[^A-Za-z]+"

# Regular expression used for replacing non-alphanum characters
REFLECTED_REPLACEMENT_REGEX = r"[^\n]{1,100}"

# Maximum time (in seconds) spent per reflective value(s) replacement
REFLECTED_REPLACEMENT_TIMEOUT = 3

# Maximum number of alpha-numerical parts in reflected regex (for speed purposes)
REFLECTED_MAX_REGEX_PARTS = 10

# Number of rows to generate inside the full union test for limited output (mustn't be too large to prevent payload length problems)
LIMITED_ROWS_TEST_NUMBER = 15

RANDOM_INTEGER_MARKER = "[RANDINT]"
RANDOM_STRING_MARKER = "[RANDSTR]"
SLEEP_TIME_MARKER = "[SLEEPTIME]"
INFERENCE_MARKER = "[INFERENCE]"
SINGLE_QUOTE_MARKER = "[SINGLE_QUOTE]"

PAYLOAD_DELIMITER = "__PAYLOAD_DELIMITER__"
BOUNDARY_BACKSLASH_MARKER = '__BACKSLASH__'
CUSTOM_INJECTION_MARK_CHAR = '*'
DEFAULT_GET_POST_DELIMITER = '&'
URI_QUESTION_MARKER = "__QUESTION_MARK__"
DYNAMICITY_MARK_LENGTH = 32
PARAMETER_AMP_MARKER = '__AMP__'
PARAMETER_SEMICOLON_MARKER = '__SEMICOLON__'
UNICODE_ENCODING = 'utf8'
HEURISTIC_CHECK_ALPHABET = ('"', '\'', ')', '(', ',', '.')
URLENCODE_CHAR_LIMIT = 2000
URLENCODE_FAILSAFE_CHARS = "()|,"
REFLECTED_VALUE_MARKER = "__REFLECTED_VALUE__"
TEXT_TAG_REGEX = r"(?si)<(abbr|acronym|b|blockquote|br|center|cite|code|dt|em|font|h\d|i|li|p|pre|q|strong|sub|sup|td|th|title|tt|u)(?!\w).*?>(?P<result>[^<]+)"



class PAYLOAD:
    SQLINJECTION = {
                        1: "boolean-based blind",
                        2: "error-based",
                        3: "inline query",
                        4: "stacked queries",
                        5: "AND/OR time-based blind",
                        6: "UNION query",
                   }

    PARAMETER = {
                    1: "Unescaped numeric",
                    2: "Single quoted string",
                    3: "LIKE single quoted string",
                    4: "Double quoted string",
                    5: "LIKE double quoted string",
                }

    RISK = {
                0: "No risk",
                1: "Low risk",
                2: "Medium risk",
                3: "High risk",
           }

    CLAUSE = {
                0: "Always",
                1: "WHERE",
                2: "GROUP BY",
                3: "ORDER BY",
                4: "LIMIT",
                5: "OFFSET",
                6: "TOP",
                7: "Table name",
                8: "Column name",
             }

    class METHOD:
        COMPARISON = "comparison"
        GREP = "grep"
        TIME = "time"
        UNION = "union"

    class TECHNIQUE:
        BOOLEAN = 1
        ERROR = 2
        QUERY = 3
        STACKED = 4
        TIME = 5
        UNION = 6

    class WHERE:
        ORIGINAL = 1
        NEGATIVE = 2
        REPLACE = 3



class PLACEMETHOD:
    GET = "GET"
    POST = "POST"
    URI = "URI"
    COOKIE = "Cookie"
    USER_AGENT = "User-Agent"
    REFERER = "Referer"
    HOST = "Host"
    CUSTOM_POST = "(custom) POST"
    CUSTOM_HEADER = "(custom) HEADER"

class PLACE:
    GET = "GET"
    POST = "POST"
    URI = "URI"
    COOKIE = "Cookie"
    USER_AGENT = "User-Agent"
    REFERER = "Referer"
    HOST = "Host"
    CUSTOM_POST = "(custom) POST"
    CUSTOM_HEADER = "(custom) HEADER"


class SORT_ORDER:
    FIRST = 0
    SECOND = 1
    THIRD = 2
    FOURTH = 3
    FIFTH = 4
    LAST = 100

class TECHNIQUE:
    BOOLEAN = 1
    ERROR = 2
    QUERY = 3
    STACKED = 4
    TIME = 5
    UNION = 6

class WHERE:
    ORIGINAL = 1
    NEGATIVE = 2
    REPLACE = 3

class DBMS(object):
    ACCESS = "Microsoft Access"
    DB2 = "IBM DB2"
    FIREBIRD = "Firebird"
    MAXDB = "SAP MaxDB"
    MSSQL = "Microsoft SQL Server"
    MYSQL = "MySQL"
    ORACLE = "Oracle"
    PGSQL = "PostgreSQL"
    SQLITE = "SQLite"
    SYBASE = "Sybase"
    HSQLDB = "HSQLDB"
    H2 = "H2"
    INFORMIX = "Informix"



# DBMS system databases
MSSQL_SYSTEM_DBS = ("Northwind", "master", "model", "msdb", "pubs", "tempdb")
MYSQL_SYSTEM_DBS = ("information_schema", "mysql", "performance_schema", "sys")
PGSQL_SYSTEM_DBS = ("information_schema", "pg_catalog", "pg_toast", "pgagent")
ORACLE_SYSTEM_DBS = ('ANONYMOUS', 'APEX_030200', 'APEX_PUBLIC_USER', 'APPQOSSYS', 'BI', 'CTXSYS', 'DBSNMP', 'DIP', 'EXFSYS', 'FLOWS_%', 'FLOWS_FILES', 'HR', 'IX', 'LBACSYS', 'MDDATA', 'MDSYS', 'MGMT_VIEW', 'OC', 'OE', 'OLAPSYS', 'ORACLE_OCM', 'ORDDATA', 'ORDPLUGINS', 'ORDSYS', 'OUTLN', 'OWBSYS', 'PM', 'SCOTT', 'SH', 'SI_INFORMTN_SCHEMA', 'SPATIAL_CSW_ADMIN_USR', 'SPATIAL_WFS_ADMIN_USR', 'SYS', 'SYSMAN', 'SYSTEM', 'WKPROXY', 'WKSYS', 'WK_TEST', 'WMSYS', 'XDB', 'XS$NULL')
SQLITE_SYSTEM_DBS = ("sqlite_master", "sqlite_temp_master")
ACCESS_SYSTEM_DBS = ("MSysAccessObjects", "MSysACEs", "MSysObjects", "MSysQueries", "MSysRelationships", "MSysAccessStorage", "MSysAccessXML", "MSysModules", "MSysModules2")
FIREBIRD_SYSTEM_DBS = ("RDB$BACKUP_HISTORY", "RDB$CHARACTER_SETS", "RDB$CHECK_CONSTRAINTS", "RDB$COLLATIONS", "RDB$DATABASE", "RDB$DEPENDENCIES", "RDB$EXCEPTIONS", "RDB$FIELDS", "RDB$FIELD_DIMENSIONS", " RDB$FILES", "RDB$FILTERS", "RDB$FORMATS", "RDB$FUNCTIONS", "RDB$FUNCTION_ARGUMENTS", "RDB$GENERATORS", "RDB$INDEX_SEGMENTS", "RDB$INDICES", "RDB$LOG_FILES", "RDB$PAGES", "RDB$PROCEDURES", "RDB$PROCEDURE_PARAMETERS", "RDB$REF_CONSTRAINTS", "RDB$RELATIONS", "RDB$RELATION_CONSTRAINTS", "RDB$RELATION_FIELDS", "RDB$ROLES", "RDB$SECURITY_CLASSES", "RDB$TRANSACTIONS", "RDB$TRIGGERS", "RDB$TRIGGER_MESSAGES", "RDB$TYPES", "RDB$USER_PRIVILEGES", "RDB$VIEW_RELATIONS")
MAXDB_SYSTEM_DBS = ("SYSINFO", "DOMAIN")
SYBASE_SYSTEM_DBS = ("master", "model", "sybsystemdb", "sybsystemprocs")
DB2_SYSTEM_DBS = ("NULLID", "SQLJ", "SYSCAT", "SYSFUN", "SYSIBM", "SYSIBMADM", "SYSIBMINTERNAL", "SYSIBMTS", "SYSPROC", "SYSPUBLIC", "SYSSTAT", "SYSTOOLS")
HSQLDB_SYSTEM_DBS = ("INFORMATION_SCHEMA", "SYSTEM_LOB")
H2_SYSTEM_DBS = ("INFORMATION_SCHEMA")
INFORMIX_SYSTEM_DBS = ("sysmaster", "sysutils", "sysuser", "sysadmin")

MSSQL_ALIASES = ("microsoft sql server", "mssqlserver", "mssql", "ms")
MYSQL_ALIASES = ("mysql", "my", "mariadb", "maria")
PGSQL_ALIASES = ("postgresql", "postgres", "pgsql", "psql", "pg")
ORACLE_ALIASES = ("oracle", "orcl", "ora", "or")
SQLITE_ALIASES = ("sqlite", "sqlite3")
ACCESS_ALIASES = ("msaccess", "access", "jet", "microsoft access")
FIREBIRD_ALIASES = ("firebird", "mozilla firebird", "interbase", "ibase", "fb")
MAXDB_ALIASES = ("maxdb", "sap maxdb", "sap db")
SYBASE_ALIASES = ("sybase", "sybase sql server")
DB2_ALIASES = ("db2", "ibm db2", "ibmdb2")
HSQLDB_ALIASES = ("hsql", "hsqldb", "hs", "hypersql")
H2_ALIASES = ("h2",)
INFORMIX_ALIASES = ("informix", "ibm informix", "ibminformix")

DBMS_DICT = {
    DBMS.MSSQL: (MSSQL_ALIASES, "python-pymssql", "https://github.com/pymssql/pymssql", "mssql+pymssql"),
    DBMS.MYSQL: (MYSQL_ALIASES, "python-pymysql", "https://github.com/PyMySQL/PyMySQL", "mysql"),
    DBMS.PGSQL: (PGSQL_ALIASES, "python-psycopg2", "http://initd.org/psycopg/", "postgresql"),
    DBMS.ORACLE: (ORACLE_ALIASES, "python cx_Oracle", "https://oracle.github.io/python-cx_Oracle/", "oracle"),
    DBMS.SQLITE: (SQLITE_ALIASES, "python-sqlite", "https://docs.python.org/2/library/sqlite3.html", "sqlite"),
    DBMS.ACCESS: (ACCESS_ALIASES, "python-pyodbc", "https://github.com/mkleehammer/pyodbc", "access"),
    DBMS.FIREBIRD: (FIREBIRD_ALIASES, "python-kinterbasdb", "http://kinterbasdb.sourceforge.net/", "firebird"),
    DBMS.MAXDB: (MAXDB_ALIASES, None, None, "maxdb"),
    DBMS.SYBASE: (SYBASE_ALIASES, "python-pymssql", "https://github.com/pymssql/pymssql", "sybase"),
    DBMS.DB2: (DB2_ALIASES, "python ibm-db", "https://github.com/ibmdb/python-ibmdb", "ibm_db_sa"),
    DBMS.HSQLDB: (HSQLDB_ALIASES, "python jaydebeapi & python-jpype", "https://pypi.python.org/pypi/JayDeBeApi/ & http://jpype.sourceforge.net/", None),
    DBMS.H2: (H2_ALIASES, None, None, None),
    DBMS.INFORMIX: (INFORMIX_ALIASES, "python ibm-db", "https://github.com/ibmdb/python-ibmdb", "ibm_db_sa"),
}


FROM_DUMMY_TABLE = {
    DBMS.ORACLE: " FROM DUAL",
    DBMS.ACCESS: " FROM MSysAccessObjects",
    DBMS.FIREBIRD: " FROM RDB$DATABASE",
    DBMS.MAXDB: " FROM VERSIONS",
    DBMS.DB2: " FROM SYSIBM.SYSDUMMY1",
    DBMS.HSQLDB: " FROM INFORMATION_SCHEMA.SYSTEM_USERS",
    DBMS.INFORMIX: " FROM SYSMASTER:SYSDUAL"
}
