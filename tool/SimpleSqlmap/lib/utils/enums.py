# Coefficient used for a time-based query delay checking (must be >= 7)
TIME_STDEV_COEFF = 2
# Minimum time response set needed for time-comparison based on standard deviation
MIN_TIME_RESPONSES = 30
# Maximum time response set used during time-comparison based on standard deviation
MAX_TIME_RESPONSES = 200
# Minimum response time that can be even considered as delayed (not a complete requirement)
MIN_VALID_DELAYED_RESPONSE = 0.5

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

