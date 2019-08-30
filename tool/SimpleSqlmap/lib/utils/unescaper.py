from lib.utils.common import AttribDict
from lib.utils.common import Backend

CHAR_INFERENCE_MARK = "%c"
EXCLUDE_UNESCAPE = ("WAITFOR DELAY ", " INTO DUMPFILE ", " INTO OUTFILE ", "CREATE ", "BULK ", "EXEC ", "RECONFIGURE ", "DECLARE ", "'%s'" % CHAR_INFERENCE_MARK)



class Unescaper(AttribDict):
    def escape(self, expression, quote=True, dbms=None):
       
        if expression is None:
            return expression

        for exclude in EXCLUDE_UNESCAPE:
            if exclude in expression:
                return expression
        

        if dbms is not None:
            return self[dbms](expression, quote=quote)
        else:
            return expression
     

unescaper = Unescaper()