#!/usr/bin/python

import os
import sys
import subprocess
import re
import ast

import pygments
from pygments.lexers import PythonLexer
from pygments.token import Token

from collections import defaultdict


LOG_LEVEL = 1


def log(msg, level=0):
    """
    Print a message with differents levels of importance
    0: trace, 1: info, 2: warn, 3: error
    """
    color = ['\033[0m', '\033[94m', '\033[93m', '\033[91m']
    if level < 0 or level > 3:
        level = 0

    if level >= LOG_LEVEL:
        print color[level] + str(msg) + '\033[0m'
        sys.stdout.flush()

magicMethods_1 = ['__new__', '__del__', '__cmp__', '__eq__', '__ne__', '__lt__',
                  '__gt__', '__le__', '__ge__', '__add__', '__sub__', '__mul__',
                  '__div__', '__and__', '__or__', '__int__', '__long__', '__float__',
                  '__str__', '__repr__', '__bool__', '__call__', '__enter__',
                  '__exit__', '__get__', '__set__', '__delete__', '__len__',
                  '__getitem__', '__setitem__', '__delitem__', '__getattr__',
                  '__setattr__', '__delattr__', '__iter__', '__contains__']

magicMethods_2 = ['__floordiv__', '__truediv__', '__mod__', '__xor__', '__pow__',
                  '__radd__', '__rsub__', '__rdiv__', '__iadd__', '__isub__',
                  '__idiv__', '__rand__', '__ror__', '__iand__', '__ior__', '__hex__',
                  '__complex__', '__oct__', '__unicode__', '__format__', '__hash__',
                  '__dir__', '__copy__', '__deepcopy__', '__getattribute__',
                  '__reversed__', '__getstate__', '__setstate__', '__reduce__',
                  '__pos__', '__neg__', '__abs__', '__invert__', '__round__']

magicMethods_3 = ['__divmod__', '__lshift__', '__rshift__', '__rfloordiv__',
                  '__rtruediv__', '__rmod__', '__rdivmod__', '__rpow__', '__rlshift__',
                  '__rrshift__', '__rxor__', '__ifloordiv__', '__itruediv__',
                  '__imod__', '__idivmod__', '__ipow__', '__ilshift__', '__irshift__',
                  '__ixor__', '__index__', '__trunc__', '__coerce__', '__sizeof__',
                  '__bytes__', '__nonzero__', '__instancecheck__', '__subclasscheck__',
                  '__missing__', '__getinitargs__', '__getnewargs__', '__reduce_ex__',
                  '__floor__', '__ceil__']


#######################################
##         INTERNAL FUNCTIONS        ##
#######################################

def _ignoreStr(str):
    pWhite = re.compile('\s+')
    pQuotes = re.compile('(\')|(\")')
    if pWhite.match(str) or pQuotes.match(str):
        return True
    else:
        return False


def _sameToken(token1, token2):
    return token1[0] is token2[0] and re.match(token2[1], token1[1])


def _findSeqInTokens(sequence, tokens):
    pos = 0
    lineNumber = 1

    for ttype, word in tokens:
        lineNumber += _getNewLines((ttype, word))
        if _sameToken((ttype, word), sequence[pos]):
            pos += 1
        elif _ignoreStr(word):
            continue
        # Check before starting again if it is the first word in the sequence
        elif _sameToken((ttype, word), sequence[0]):
            pos = 1
        else:
            pos = 0
        # End?
        if pos >= len(sequence):
            break
    else:
        return -1
    return lineNumber


def _getIndent(line):
    return len(line) - len(line.lstrip(' '))


def _beginTry(line):
    return line.strip().startswith('try')


def _findOneToken(tokenToFind, code):
    """
    Find a token in the code and returns a list of lines where it was found
    """
    lexer = PythonLexer()
    tokens = pygments.lex(code, lexer)
    lineNumber = 1
    whereFound = []

    for token in tokens:
        lineNumber += _getNewLines(token)
        if _sameToken(token, tokenToFind):
            whereFound.append(lineNumber)
    return whereFound


def _getNewLines(token):
    numlines = len(token[1].split('\n')) - 1
    if numlines < 0:
        raise Exception('What happen with this token?<' + str(token) + '>')
    return numlines


class PythonIdiom():
    """
    Class for storing one idiom and where it was found in a file
    and from who
    name: name of the idiom
    where: list of dictionaries with line, author, and other information.
    """
    def __init__(self, name):
        self.name = name
        self.where = []

    def __len__(self):
        return len(self.where)

    def __str__(self):
        return '{Name:%s, where:%s}' % (self.name, str(self.where))

    def addNew(self, line, author='', otherInfo={}):
        dictSave = {"line": line, "author": author}
        for key in otherInfo:
            dictSave[key] = otherInfo[key]
        self.where.append(dictSave)

    def getLines(self):
        """ Return a list with the lines where it was found """
        return [item["line"] for item in self.where]


##################################
##     FUNCTIONS FOR IDIOMS     ##
##################################

def findMagicMethods(code):
    """
    Search magic methods in the code and returns a list of how many have
    been found, what kind of dificult it has and wich where
    Documentation: http://www.rafekettler.com/magicmethods.html
                   Python Pocket Reference page 88
    """
    lexer = PythonLexer()
    tokens = pygments.lex(code, lexer)
    lineNumber = 1
    methodsFound = []
    methodsIdiom1 = PythonIdiom('idiomMethods1')
    methodsIdiom2 = PythonIdiom('idiomMethods2')
    methodsIdiom3 = PythonIdiom('idiomMethods3')

    for ttype, word in tokens:
        lineNumber += _getNewLines((ttype, word))
        if ttype is Token.Name.Function.Magic:
            if word in magicMethods_1:
                methodsIdiom1.addNew(lineNumber, otherInfo={'method': word})
                methodsFound.append(word)
            elif word in magicMethods_2:
                methodsIdiom2.addNew(lineNumber, otherInfo={'method': word})
                methodsFound.append(word)
            elif word in magicMethods_3:
                methodsIdiom3.addNew(lineNumber, otherInfo={'method': word})
                methodsFound.append(word)

    log("MagicMethods: %s" % str(methodsFound))
    return [methodsIdiom1, methodsIdiom2, methodsIdiom3]


def findDecorators(code):
    """
    Look for decorators @
    Documentation: Python Pocket Reference page 67
    Returns a tuple with general decorators, classmethod and staticmethod
    """
    decorators = PythonIdiom('decorator')
    # builtins decorators
    decorator_class = PythonIdiom('classmethod')
    decorator_static = PythonIdiom('staticmethod')
    decorator_total_ordering = PythonIdiom('functools.total_ordering')

    lexer = PythonLexer()
    tokens = pygments.lex(code, lexer)
    lineNumber = 1
    for ttype, word in tokens:
        lineNumber += _getNewLines((ttype, word))
        if ttype is Token.Name.Decorator:
            if word == "@classmethod":
                decorator_class.addNew(lineNumber)
            elif word == "@staticmethod":
                decorator_static.addNew(lineNumber)
            elif word == "@total_ordering":
                decorator_total_ordering.addNew(lineNumber)
            else:
                decorators.addNew(lineNumber, otherInfo={'method': word})
    log("Decorators found in lines: " + str(decorators.getLines()))
    log("@classmethod found in lines: " + str(decorator_class.getLines()))
    log("@staticmethod found in lines: " + str(decorator_static.getLines()))
    log("@total_ordering found in lines: " + str(decorator_total_ordering.getLines()))
    return decorators, decorator_class, decorator_static, decorator_total_ordering


def findMain(code):
    """
    Look for the existence of if __name__ == '__main__'
    Documentation: https://docs.python.org/2/tutorial/modules.html in 6.1.1
    """
    found = False
    pos = 0
    lexer = PythonLexer()

    tokens_1 = pygments.lex(code, lexer)
    tokens_2 = pygments.lex(code, lexer)

    sequence_1 = [(Token.Keyword, '^if$'),
                  (Token.Name.Variable.Magic, '^__name__$'),
                  (Token.Operator, '^==$'),
                  (Token.Literal.String.Double, '^__main__$'),
                  (Token.Punctuation, '^:$')]

    sequence_2 = [(Token.Keyword, '^if$'),
                  (Token.Name.Variable.Magic, '^__name__$'),
                  (Token.Operator, '^==$'),
                  (Token.Literal.String.Single, '^__main__$'),
                  (Token.Punctuation, '^:$')]

    mainIdiom = PythonIdiom('ifNameMain')

    lineNum = _findSeqInTokens(sequence_1, tokens_1)
    if lineNum < 0:
        lineNum = _findSeqInTokens(sequence_2, tokens_2)
    if lineNum > 0:
        mainIdiom.addNew(lineNum)
    log("If name main found in lines: " + str(mainIdiom.getLines()))
    return mainIdiom


def findListCompr(code):
    """
    Look for list comprehension
    Documentation: Python pocket reference page 38
    """
    comprIdiom = PythonIdiom('listComprehension')
    try:
        tree = ast.parse(code)
    except (SyntaxError, TypeError, ValueError):
        log("Couldn't analyze list comprehension", 2)
        return comprIdiom
    listComps = [node for node in ast.walk(tree) if type(node) is ast.ListComp]

    for compr in listComps:
        comprIdiom.addNew(compr.lineno)
    log("List comprehension found in lines: " + str(comprIdiom.getLines()))
    return comprIdiom


def findGenerators(code):
    """
    Look for generators
    Documentation: Fluent Python page 25
    """
    generatorIdiom = PythonIdiom('generators')

    try:
        tree = ast.parse(code)
    except (SyntaxError, TypeError, ValueError):
        log("Couldn't analyze generators", 2)
        return generatorIdiom
    generators = [node for node in ast.walk(tree)
                  if type(node) is ast.GeneratorExp]

    for generator in generators:
        generatorIdiom.addNew(generator.lineno)
    log("Generators found in lines: " + str(generatorIdiom.getLines()))
    return generatorIdiom


def findCallFunctEqual(code):
    """
    Check if calls any function with Keyword like foo(bar="foobar")
    Documentation: https://youtu.be/OSGv2VnC0go?t=31m10s
    """

    seqCallFunct = [(Token.Name, '^\w+$'),
                    (Token.Punctuation, '^\($')]

    tokenEndFunct = (Token.Punctuation, '^\)$')

    seqFind = [(Token.Name, '^\w+$'),
               (Token.Operator, '^=$')]

    lexer = PythonLexer()
    tokens = pygments.lex(code, lexer)

    callEqIdiom = PythonIdiom('equalFunctionCall')
    lineNumber = 1

    pos = 0
    while True:
        # Look for function call
        lineAux = _findSeqInTokens(seqCallFunct, tokens)
        if lineAux > 0:
            lineNumber += lineAux - 1
            for ttype, word in tokens:
                lineNumber += _getNewLines((ttype, word))
                if _sameToken((ttype, word), tokenEndFunct):
                    break
                if _sameToken((ttype, word), seqFind[pos]):
                    pos += 1
                elif _ignoreStr(word):
                    continue
                else:
                    pos = 0
                # End?
                if pos >= len(seqFind):
                    pos = 0
                    callEqIdiom.addNew(lineNumber)
        else:
            break
    log('call function equal found in lines ' + str(callEqIdiom.getLines()))
    return callEqIdiom


def findNamedtuple(code):
    """
    Find namedTuples in the code
    Documentation: https://youtu.be/OSGv2VnC0go?t=32m18s
                   https://docs.python.org/2/library/collections.html#namedtuple-factory-function-for-tuples-with-named-fields
                   Fluent Python page 30
    """
    tokenNamedtuple = (Token.Name, u'namedtuple')
    namedTupleIdiom = PythonIdiom('namedTuple')
    for lineFound in _findOneToken(tokenNamedtuple, code):
        namedTupleIdiom.addNew(lineFound)
    log("namedtuple found in lines " + str(namedTupleIdiom.getLines()))
    return namedTupleIdiom


def findYield(code):
    """
    Find 'yield' statement in the code
    Documentation: Introducing to Python page 98 (Generators)
                   Fluent Python page 415 (How a generator function works)
    """
    tokenYield = (Token.Keyword, '^yield$')
    yieldIdiom = PythonIdiom('yield')
    for lineFound in _findOneToken(tokenYield, code):
        yieldIdiom.addNew(lineFound)
    log("yield found in lines: " + str(yieldIdiom.getLines()))
    return yieldIdiom


def findWith(code):
    """
    Find 'with' statement in the code
    Documentation:
        http://preshing.com/20110920/the-python-with-statement-by-example
        Fluent Python page 452 (Context managers and 'with' blocks)
        https://www.python.org/dev/peps/pep-0343/

    """
    tokenWith = (Token.Keyword, '^with$')
    withIdiom = PythonIdiom('with')
    for lineFound in _findOneToken(tokenWith, code):
        withIdiom.addNew(lineFound)
    log("with found in lines: " + str(withIdiom.getLines()))
    return withIdiom


def findLambda(code):
    """
    Find 'lambda' statement in the code
    Documentation:
       http://www.secnetix.de/olli/Python/lambda_functions.hawk
       Introducing Python page 96. (Anonymous Functions: the lambda() Function)
    """
    tokenLambda = (Token.Keyword, '^lambda$')
    lambdaIdiom = PythonIdiom('lambda')
    for lineFound in _findOneToken(tokenLambda, code):
        lambdaIdiom.addNew(lineFound)
    log("lambda found in lines: " + str(lambdaIdiom.getLines()))
    return lambdaIdiom


def findNestedFunctions(code):
    """
    Look for closures in the code
    Documentation: https://www.python.org/dev/peps/pep-0227
    """
    inFunct = False
    lineNum = 0
    indentFunct = 0
    indentLine = 0
    nestedFuncIdiom = PythonIdiom('NestedFunction')

    for line in code.split('\n'):
        lineNum += 1
        indentLine = _getIndent(line)
        if inFunct:
            if indentLine <= indentFunct:
                inFunct = False
                indentFunct = 0
            elif line.strip().startswith('def ') and indentLine > indentFunct:
                nestedFuncIdiom.addNew(lineNum)
        else:
            if line.strip().startswith('def '):
                inFunct = True
                indentFunct = indentLine

    log("nested function found in lines " + str(nestedFuncIdiom.getLines()))
    return nestedFuncIdiom


def findAssert(code):
    """
    Find 'assert' statement in the code
    Documentation: https://wiki.python.org/moin/UsingAssertionsEffectively
                   https://docs.python.org/2/reference/simple_stmts.html#the-assert-statement
    """
    tokenAssert = (Token.Keyword, '^assert$')
    assertIdiom = PythonIdiom('assert')
    for lineFound in _findOneToken(tokenAssert, code):
        assertIdiom.addNew(lineFound)
    log("assert found in lines {0}".format(assertIdiom.getLines()))
    return assertIdiom


def findFinally(code):
    """
    Find 'finally' statement in the code
    Documentation:
       https://docs.python.org/2/tutorial/errors.html#defining-clean-up-actions
    """
    tokenFinally = (Token.Keyword, '^finally$')
    finallyIdiom = PythonIdiom('finally')
    for lineFound in _findOneToken(tokenFinally, code):
        finallyIdiom.addNew(lineFound)
    log("finally found in lines {0}".format(finallyIdiom.getLines()))
    return finallyIdiom


def findDocstring(code):
    """Find the use of documentation in the functions, classes or script
    Documentation: https://www.python.org/dev/peps/pep-0257/
    """
    lexer = PythonLexer()
    lexer.add_filter('tokenmerge')

    classDefToken = (Token.Keyword, '^class$')
    functDefToken = (Token.Keyword, '^def$')
    tokens = pygments.lex(code, lexer)

    docIdiom = PythonIdiom('docstring')
    docstringFound = defaultdict(int)
    typeDoc = 'module'
    lineNumber = 1

    for ttype, word in tokens:
        if _sameToken((ttype, word), classDefToken):
            typeDoc = 'class'
        elif _sameToken((ttype, word), functDefToken):
            typeDoc = 'function'
        elif ttype == Token.Literal.String.Doc:
            docstringFound[typeDoc] += 1
            docIdiom.addNew(lineNumber)
        lineNumber += _getNewLines((ttype, word))

    for typeDoc in docstringFound:
        log("type %s: %d found" % (typeDoc, docstringFound[typeDoc]))
    log('DocString found in lines: ' + str(docIdiom.getLines()))
    return docIdiom


def findUpdateVariables1Line(code):
    """
    Look for lines of code like this: 'x, y = 0, 1' or 'x, y = y, x+y'
    """
    lexer = PythonLexer()
    tokens = pygments.lex(code, lexer)

    linesFound = []
    assignIdiom = PythonIdiom('assignOneLine')
    # Tokens variables
    nameToken = (Token.Name, '^\w+$')
    equalToken = (Token.Operator, '^\=$')
    newLineToken = (Token.Text, '\n')
    commaToken = (Token.Punctuation, '^,$')

    # To advoid mistakes, I count the variables before/after the equal
    numVarPrevEqual = 0
    numVarPostEqual = 0
    numCommas = 0
    beforeEqual = True
    actualLine = ''
    ignoreLine = False
    lineNumber = 1

    for ttype, word in tokens:
        if not _ignoreStr(word):
            actualLine += word.encode('utf-8')
        lineNumber += _getNewLines((ttype, word))
        if _sameToken((ttype, word), newLineToken):
            beforeEqual = True
            if numVarPrevEqual == numVarPostEqual and numVarPrevEqual > 1:
                if not ignoreLine:
                    linesFound.append(actualLine)
                    # -1 because waits until the line finish:
                    assignIdiom.addNew(lineNumber-1)
            actualLine = ''
            numVarPrevEqual, numVarPostEqual, numCommas = 0, 0, 0
            ignoreLine = False
            continue

        if ignoreLine:
            continue

        if _sameToken((ttype, word), equalToken):
            if not beforeEqual:
                ignoreLine = True
            beforeEqual = False
            numCommas = 0
        elif _sameToken((ttype, word), commaToken):
            numCommas += 1

        if beforeEqual:
            if _sameToken((ttype, word), nameToken) and (numCommas == numVarPrevEqual):
                numVarPrevEqual += 1
        else:
            if re.match('\w+', word.encode('utf-8')) and (numCommas == numVarPostEqual):
                numVarPostEqual += 1
    log("Update in 1 line. Found: " + str(linesFound))
    log("Update in 1 line found in lines " + str(assignIdiom.getLines()))
    return assignIdiom


def findDeque(code):
    """
    Find the use of deque in the code
    Documentation: Fluent Python page 54
                   https://docs.python.org/2/library/collections.html#collections.deque
                   https://pymotw.com/2/collections/deque.html
    """
    dequeToken = (Token.Name, '^deque$')
    dequeIdiom = PythonIdiom('deque')
    for lineFound in _findOneToken(dequeToken, code):
        dequeIdiom.addNew(lineFound)
    log("deque found in lines {0}".format(dequeIdiom.getLines()))
    return dequeIdiom


def findDefaultDict(code):
    """
    Find the use of default dict in the code
    Documentation:
     https://docs.python.org/2/library/collections.html#collections.defaultdict
    """
    dictToken = (Token.Name, '^defaultdict$')
    defDictIdiom = PythonIdiom('defaultdict')
    for lineFound in _findOneToken(dictToken, code):
        defDictIdiom.addNew(lineFound)
    log("defaultdict found in lines {0}".format(defDictIdiom.getLines()))
    return defDictIdiom


def findOrderedDict(code):
    """
    Find the use of orderedDict in the code
    Documentation:
     https://docs.python.org/2/library/collections.html#collections.OrderedDict
    """
    dictToken = (Token.Name, '^OrderedDict$')
    ordDictIdiom = PythonIdiom('orderecdict')
    for lineFound in _findOneToken(dictToken, code):
        ordDictIdiom.addNew(lineFound)
    log("orderedDict found in lines {0}".format(ordDictIdiom.getLines()))
    return ordDictIdiom


def findUseMapFilterReduce(code):
    """
    Find the use of map, filter and reduce builtins in the code.
    A better option is the use of generators and list comprehensions
    Documentation: Fluent Python page 142
       https://docs.python.org/2/library/functions.html#map
       https://docs.python.org/2/library/functions.html#filter
       https://docs.python.org/2/library/functions.html#reduce
    """
    filterToken = (Token.Name.Builtin, '^filter$')
    mapToken = (Token.Name.Builtin, '^map$')
    reduceToken = (Token.Name.Builtin, '^reduce$')
    tokensFound = {'filter': 0,
                   'map': 0,
                   'reduce': 0}

    lexer = PythonLexer()
    lexer.add_filter('tokenmerge')
    tokens = pygments.lex(code, lexer)
    lineNumber = 1

    mapIdiom = PythonIdiom('map')
    filterIdiom = PythonIdiom('filter')
    reduceIdiom = PythonIdiom('reduce')

    for token in tokens:
        lineNumber += _getNewLines(token)
        if _sameToken(token, filterToken):
            tokensFound['filter'] += 1
            filterIdiom.addNew(lineNumber)
        elif _sameToken(token, reduceToken):
            tokensFound['reduce'] += 1
            reduceIdiom.addNew(lineNumber)
        elif _sameToken(token, mapToken):
            tokensFound['map'] += 1
            mapIdiom.addNew(lineNumber)
    log('filter found in lines: ' + str(filterIdiom.getLines()))
    log('map found in lines: ' + str(mapIdiom.getLines()))
    log('reduce found in lines: ' + str(reduceIdiom.getLines()))
    return mapIdiom, filterIdiom, reduceIdiom


def findZip(code):
    """
    Find the use of zip in the code
    Documentation:
     https://docs.python.org/2/library/functions.html#zip
    """
    zip_token = (Token.Name.Builtin, '^zip$')
    zip_idiom = PythonIdiom('zip')
    for line_found in _findOneToken(zip_token, code):
        zip_idiom.addNew(line_found)
    log("zip found in lines {0}".format(zip_idiom.getLines()))
    return zip_idiom


# itertools idioms

def find_izip(code):
    """
    Find the use of izip in the code
    Documentation:

    """
    izip_token = (Token.Name, '^izip$')
    izip_idiom = PythonIdiom('izip')
    for line_found in _findOneToken(izip_token, code):
        izip_idiom.addNew(line_found)
    log("izip found in lines {0}".format(izip_idiom.getLines()))
    return izip_idiom

def find_izip_longest(code):
    """
    Find the use of izip_longest in the code
    Documentation:

    """
    izip_longest_token = (Token.Name, '^izip_longest$')
    izip_longest_idiom = PythonIdiom('izip_longest')
    for line_found in _findOneToken(izip_longest_token, code):
        izip_longest_idiom.addNew(line_found)
    log("izip_longest found in lines {0}".format(izip_longest_idiom.getLines()))
    return izip_longest_idiom

def find_imap(code):
    """
    Find the use of imap in the code
    Documentation:

    """
    imap_token = (Token.Name, '^imap$')
    imap_idiom = PythonIdiom('imap')
    for line_found in _findOneToken(imap_token, code):
        imap_idiom.addNew(line_found)
    log("imap found in lines {0}".format(imap_idiom.getLines()))
    return imap_idiom

def find_startmap(code):
    """
    Find the use of startmap in the code
    Documentation:

    """
    startmap_token = (Token.Name, '^startmap$')
    startmap_idiom = PythonIdiom('startmap')
    for line_found in _findOneToken(startmap_token, code):
        startmap_idiom.addNew(line_found)
    log("startmap found in lines {0}".format(startmap_idiom.getLines()))
    return startmap_idiom

def find_tee(code):
    """
    Find the use of tee in the code
    Documentation:

    """
    tee_token = (Token.Name, '^tee$')
    tee_idiom = PythonIdiom('tee')
    for line_found in _findOneToken(tee_token, code):
        tee_idiom.addNew(line_found)
    log("tee found in lines {0}".format(tee_idiom.getLines()))
    return tee_idiom

def find_groupby(code):
    """
    Find the use of groupby in the code
    Documentation:

    """
    groupby_token = (Token.Name, '^groupby$')
    groupby_idiom = PythonIdiom('groupby')
    for line_found in _findOneToken(groupby_token, code):
        groupby_idiom.addNew(line_found)
    log("groupby found in lines {0}".format(groupby_idiom.getLines()))
    return groupby_idiom

# functools idioms

def find_partial(code):
    """
    Find the use of partial in the code
    Documentation:

    """
    partial_token = (Token.Name, '^partial$')
    partial_idiom = PythonIdiom('partial')
    for line_found in _findOneToken(partial_token, code):
        partial_idiom.addNew(line_found)
    log("partial found in lines {0}".format(partial_idiom.getLines()))
    return partial_idiom



#######################
##    Anti-idioms    ##
#######################

def checkNotRange(code):
    """
    Check if there is: for xx in [0,1,2] instead of for xxx in (x)range
    Documentation: https://youtu.be/OSGv2VnC0go?t=3m4s
    """
    sequence = [(Token.Keyword, '^for$'),
                (Token.Name, '^\w+$'),
                (Token.Operator.Word, '^in$'),
                (Token.Punctuation, '^\[$'),
                (Token.Literal.Number.Integer, '^\d$')]

    lexer = PythonLexer()
    lexer.add_filter('tokenmerge')
    tokens = pygments.lex(code, lexer)
    notRangeIdiom = PythonIdiom('notRange')

    lineNumber = 1
    while True:
        lineAux = _findSeqInTokens(sequence, tokens)
        if lineAux < 0:
            break
        lineNumber += lineAux - 1
        notRangeIdiom.addNew(lineNumber)
    log("badForIn found in lines {0}".format(notRangeIdiom.getLines()))
    return notRangeIdiom


def findLargeTry(code):
    """
    Look for a large try except, this is BAD
    """
    longTryIdiom = PythonIdiom('longTry')

    inTry = False
    linesLength = 0
    indentTry = 0
    lineNumber = 0
    LONG_TRY_LENGTH = 5

    for line in code.split('\n'):
        lineNumber += 1
        if not inTry and _beginTry(line):
            inTry = True
            indentTry = _getIndent(line)
        elif inTry:
            indentLine = _getIndent(line)
            # Could be an empty line:
            if indentLine > indentTry or indentLine < indentTry:
                linesLength += 1
            elif indentLine == indentTry:
                if linesLength > LONG_TRY_LENGTH:
                    longTryIdiom.addNew(lineNumber - linesLength)
                inTry = False
                linesLength = 0
    log("Large try found in lines: %s" % str(longTryIdiom.getLines()))
    return longTryIdiom


def checkBadLoopCollect(code):
    """
    Look for bad loop like 'for i in range(len(list))'
    Documentation: https://youtu.be/OSGv2VnC0go?t=4m47s
    """
    sequence = [(Token.Keyword, '^for$'),
                (Token.Name, '^\w+$'),
                (Token.Operator.Word, '^in$'),
                (Token.Name.Builtin, '^range$|^xrange$'),
                (Token.Punctuation, '^\($'),
                (Token.Name.Builtin, '^len$'),
                (Token.Punctuation, '^\($'),
                (Token.Name, '^\w+$')]
    lexer = PythonLexer()
    lexer.add_filter('tokenmerge')
    tokens = pygments.lex(code, lexer)
    badLoopIdiom = PythonIdiom('badLoop')

    lineNumber = 1
    while True:
        lineAux = _findSeqInTokens(sequence, tokens)
        if lineAux < 0:
            break
        lineNumber += lineAux - 1
        badLoopIdiom.addNew(lineNumber)
    log("badLoopCollect found in lines {0}".format(badLoopIdiom.getLines()))

    return badLoopIdiom


def findBadUseImport(code):
    """
    Find when use from foo import *
    Documentation:
    http://python.net/~goodger/projects/pycon/2007/idiomatic/handout.html#importing
    https://docs.python.org/2/howto/doanddont.html#from-module-import
    """
    sequence = [(Token.Keyword.Namespace, '^from$'),
                (Token.Name.Namespace, '.*'),
                (Token.Keyword.Namespace, '^import$'),
                (Token.Operator, '\*')]
    lexer = PythonLexer()
    lexer.add_filter('tokenmerge')
    tokens = pygments.lex(code, lexer)
    badUseImport = PythonIdiom('badImport')

    lineNumber = 1
    while True:
        lineAux = _findSeqInTokens(sequence, tokens)
        if lineAux < 0:
            break
        lineNumber += lineAux - 1
        badUseImport.addNew(lineNumber)
    log("badUseImport found in lines {0}".format(badUseImport.getLines()))

    return badUseImport


def getAuthor(blameData_list, regexpr, line):
    if len(blameData_list) < line:
        log("git blame data error:{0} < {0}".format(len(blameData_list), line))
        return ''

    matched = regexpr.search(blameData_list[line-1])
    if matched:
        email = matched.groups()[0]
        lineBlame = matched.groups()[1]
        if int(lineBlame) != line:
            log("Git blame line error:{0}!={1}".format(lineBlame, line))
    else:
        log("Email not found in line number {0}".format(str(line)), 3)
        email = ''
    return email


def getGitBlame(filepath):
    """
    Guiven a file from a git project, return the tuple (data, error)
    """
    currentDir = os.getcwd()
    fileName = filepath.split('/')[-1]
    fileLocation = '/'.join(filepath.split('/')[:-1])
    if fileLocation:
        os.chdir(fileLocation)

    command = 'git blame -e'.split(' ')
    command.append(fileName)
    proc = subprocess.Popen(command,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    (data, error) = proc.communicate()
    os.chdir(currentDir)
    return (data, error)


def completeAnalysis(filepath):
    with open(filepath, 'rt') as file:
        code = file.read()

    # Lists of 'idioms and anti-idioms' objects
    results = []
    resultsAnti = []

    # Idioms
    for idiom in findMagicMethods(code):
        results.append(idiom)
    results.append(findMain(code))
    results.extend(findDecorators(code))
    results.append(findListCompr(code))
    results.append(findGenerators(code))
    results.append(findCallFunctEqual(code))
    results.append(findNamedtuple(code))
    results.append(findUpdateVariables1Line(code))
    results.append(findYield(code))
    results.append(findWith(code))
    results.append(findLambda(code))
    results.append(findNestedFunctions(code))
    results.append(findAssert(code))
    results.append(findFinally(code))
    results.append(findDocstring(code))
    results.append(findDeque(code))
    results.append(findDefaultDict(code))
    results.append(findOrderedDict(code))
    results.extend(findUseMapFilterReduce(code))
    results.append(findZip(code))
    results.append(find_izip(code))
    results.append(find_izip_longest(code))
    results.append(find_imap(code))
    results.append(find_startmap(code))
    results.append(find_tee(code))
    results.append(find_groupby(code))
    results.append(find_partial(code))

    # Anti-idioms
    resultsAnti.append(findLargeTry(code))
    resultsAnti.append(checkBadLoopCollect(code))
    resultsAnti.append(checkNotRange(code))
    resultsAnti.append(findBadUseImport(code))

    # get the info of who writes the lines
    # I do this at the end because of performance issues
    print "Doing git blame..."
    data, error = getGitBlame(filepath)
    if error:
        log('git blame error:' + error, 3)
    elif data:
        data_list = data.splitlines()
        # compile reg_expr
        regexpr_author = re.compile('\w+\s+\(<(.+@.+\..+)>\s+\d+\-\d+\-\d+ \d+\:\d+\:\d+ [\+\-]\d+\s+(\d+)\)')
        print "lines: %d" % len(data_list)
        numresults = 0
        for idiom in results:
            for one_idiom in idiom.where:
                one_idiom["author"] = getAuthor(data_list, regexpr_author, one_idiom["line"])
                numresults += 1
                print "\r" + str(numresults),
                sys.stdout.flush()

        for anti_idiom in resultsAnti:
            for one_anti_idiom in anti_idiom.where:
                one_anti_idiom["author"] = getAuthor(data_list, regexpr_author, one_anti_idiom["line"])
                numresults += 1
                print "\r" + str(numresults),
                sys.stdout.flush()

    return (results, resultsAnti)


def _main():
    (idioms, anti_idioms) = completeAnalysis(sys.argv[1])
    log("*------*------* IDIOMS *------*------*")
    for idiom in idioms:
        log(idiom, 1)
    log("*------*------* ANTI-IDIOMS *------*------*")
    for anti_idiom in anti_idioms:
        log(anti_idiom, 1)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit("Usage: python pythonic.py python_file")

    _main()
