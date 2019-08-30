from thirdparty import six
from lib.config import conf, kb

def configUnion(char=None, columns=None):
    def _configUnionChar(char):
        if not isinstance(char, six.string_types):
            return

        kb.uChar = char

        if conf.uChar is not None:
            kb.uChar = char.replace("[CHAR]", conf.uChar if conf.uChar.isdigit() else "'%s'" % conf.uChar.strip("'"))

    def _configUnionCols(columns):
        if not isinstance(columns, six.string_types):
            return

        columns = columns.replace(" ", "")
        if "-" in columns:
            colsStart, colsStop = columns.split("-")
        else:
            colsStart, colsStop = columns, columns

        if not colsStart.isdigit() or not colsStop.isdigit():
            print ("--union-cols must be a range of integers")

        conf.uColsStart, conf.uColsStop = int(colsStart), int(colsStop)

        if conf.uColsStart > conf.uColsStop:
            errMsg = "--union-cols range has to be from lower to "
            errMsg += "higher number of columns"
            print (errMsg)

    _configUnionChar(char)
    _configUnionCols(conf.uCols or columns)
