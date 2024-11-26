"""
SimpleEval - (C) 2013-2023 Daniel Fairhead
-------------------------------------

An short, easy to use, safe and reasonably extensible expression evaluator.
Designed for things like in a website where you want to allow the user to
generate a string, or a number from some other input, without allowing full
eval() or other unsafe or needlessly complex linguistics.

-------------------------------------

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

-------------------------------------

Initial idea copied from J.F. Sebastian on Stack Overflow
( http://stackoverflow.com/a/9558001/1973500 ) with
modifications and many improvements.

-------------------------------------
Contributors:
- corro (Robin Baumgartner) (py3k)
- dratchkov (David R) (nested dicts)
- marky1991 (Mark Young) (slicing)
- T045T (Nils Berg) (!=, py3kstr, obj.
- perkinslr (Logan Perkins) (.__globals__ or .func_ breakouts)
- impala2 (Kirill Stepanov) (massive _eval refactor)
- gk (ugik) (Other iterables than str can DOS too, and can be made)
- daveisfera (Dave Johansen) 'not' Boolean op, Pycharm, pep8, various other fixes
- xaled (Khalid Grandi) method chaining correctly, double-eval bugfix.
- EdwardBetts (Edward Betts) spelling correction.
- charlax (Charles-Axel Dein charlax) Makefile and cleanups
- mommothazaz123 (Andrew Zhu) f"string" support, Python 3.8 support
- lubieowoce (Uryga) various potential vulnerabilities
- JCavallo (Jean Cavallo) names dict shouldn't be modified
- Birne94 (Daniel Birnstiel) for fixing leaking generators, star expressions
- patricksurry (Patrick Surry) or should return last value, even if falsy.
- shughes-uk (Samantha Hughes) python w/o 'site' should not fail to import.
- KOLANICH packaging / deployment / setup help & << + >> & other bit ops
- graingert (Thomas Grainger) packaging / deployment / setup help
- bozokopic (Bozo Kopic) Memory leak fix
- daxamin (Dax Amin) Better error for attempting to eval empty string
- smurfix (Matthias Urlichs) Allow clearing functions / operators / etc completely

-------------------------------------
Basic Usage:

>>> s = SimpleEval()
>>> s.eval("20 + 30")
50

You can add your own functions easily too:

if file.txt contents is "11"

>>> def get_file():
...     with open("file.txt", 'r') as f:
...         return f.read()

>>> s.functions["get_file"] = get_file
>>> s.eval("int(get_file()) + 31")
42

For more information, see the full package documentation on pypi, or the github
repo.

-----------

If you don't need to re-use the evaluator (with it's names, functions, etc),
then you can use the simple_eval() function:

>>> simple_eval("21 + 19")
40

You can pass names, operators and functions to the simple_eval function as
well:

>>> simple_eval("40 + two", names={"two": 2})
42

"""

import ast
import operator as op
import sys
import warnings
from random import random

PYTHON3 = sys.version_info[0] == 3
PYTHON35 = PYTHON3 and sys.version_info > (3, 5)

########################################
# Module wide 'globals'

MAX_STRING_LENGTH = 100000
MAX_COMPREHENSION_LENGTH = 10000
MAX_POWER = 4000000  # highest exponent
MAX_SHIFT = 10000  # highest << or >> (lshift / rshift)
MAX_SHIFT_BASE = int(sys.float_info.max)  # highest on left side of << or >>
DISALLOW_PREFIXES = ["_", "func_"]
DISALLOW_METHODS = ["format", "format_map", "mro"]

# Disallow functions:
# This, strictly speaking, is not necessary.  These /should/ never be accessable anyway,
# if DISALLOW_PREFIXES and DISALLOW_METHODS are all right.  This is here to try and help
# people not be stupid.  Allowing these functions opens up all sorts of holes - if any of
# their functionality is required, then please wrap them up in a safe container.  And think
# very hard about it first.  And don't say I didn't warn you.
# builtins is a dict in python >3.6 but a module before
DISALLOW_FUNCTIONS = {type, isinstance, eval, getattr, setattr, repr, compile, open}
if hasattr(__builtins__, "help") or (
    hasattr(__builtins__, "__contains__") and "help" in __builtins__  # type: ignore
):
    # PyInstaller environment doesn't include this module.
    DISALLOW_FUNCTIONS.add(help)


if PYTHON3:
    # exec is not a function in Python2...
    exec("DISALLOW_FUNCTIONS.add(exec)")  # pylint: disable=exec-used


########################################
# Exceptions:


class InvalidExpression(Exception):
    """Generic Exception"""

    pass


class FunctionNotDefined(InvalidExpression):
    """sorry! That function isn't defined!"""

    def __init__(self, func_name, expression):
        self.message = "Function '{0}' not defined," " for expression '{1}'.".format(
            func_name, expression
        )
        setattr(self, "func_name", func_name)  # bypass 2to3 confusion.
        self.expression = expression

        super(InvalidExpression, self).__init__(self.message)


class NameNotDefined(InvalidExpression):
    """a name isn't defined."""

    def __init__(self, name, expression):
        self.name = name
        self.message = "'{0}' is not defined for expression '{1}'".format(name, expression)
        self.expression = expression

        super(InvalidExpression, self).__init__(self.message)


class AttributeDoesNotExist(InvalidExpression):
    """attribute does not exist"""

    def __init__(self, attr, expression):
        self.message = "Attribute '{0}' does not exist in expression '{1}'".format(
            attr, expression
        )
        self.attr = attr
        self.expression = expression

        super(InvalidExpression, self).__init__(self.message)


class OperatorNotDefined(InvalidExpression):
    """operator does not exist"""

    def __init__(self, attr, expression):
        self.message = "Operator '{0}' does not exist in expression '{1}'".format(attr, expression)
        self.attr = attr
        self.expression = expression

        super(InvalidExpression, self).__init__(self.message)


class FeatureNotAvailable(InvalidExpression):
    """What you're trying to do is not allowed."""

    pass


class NumberTooHigh(InvalidExpression):
    """Sorry! That number is too high. I don't want to spend the
    next 10 years evaluating this expression!"""

    pass


class IterableTooLong(InvalidExpression):
    """That iterable is **way** too long, baby."""

    pass


class AssignmentAttempted(UserWarning):
    """Assignment not allowed in SimpleEval"""

    pass


class MultipleExpressions(UserWarning):
    """Only the first expression parsed will be used"""

    pass


########################################
# Default simple functions to include:


def random_int(top):
    """return a random int below <top>"""

    return int(random() * top)


def safe_power(a, b):  # pylint: disable=invalid-name
    """a limited exponent/to-the-power-of function, for safety reasons"""

    if abs(a) > MAX_POWER or abs(b) > MAX_POWER:
        raise NumberTooHigh("Sorry! I don't want to evaluate {0} ** {1}".format(a, b))
    return a**b


def safe_mult(a, b):  # pylint: disable=invalid-name
    """limit the number of times an iterable can be repeated..."""

    if hasattr(a, "__len__") and b * len(a) > MAX_STRING_LENGTH:
        raise IterableTooLong("Sorry, I will not evalute something that long.")
    if hasattr(b, "__len__") and a * len(b) > MAX_STRING_LENGTH:
        raise IterableTooLong("Sorry, I will not evalute something that long.")

    return a * b


def safe_add(a, b):  # pylint: disable=invalid-name
    """iterable length limit again"""

    if hasattr(a, "__len__") and hasattr(b, "__len__"):
        if len(a) + len(b) > MAX_STRING_LENGTH:
            raise IterableTooLong(
                "Sorry, adding those two together would" " make something too long."
            )
    return a + b


def safe_rshift(a, b):  # pylint: disable=invalid-name
    """rshift, but with input limits"""
    if abs(b) > MAX_SHIFT or abs(a) > MAX_SHIFT_BASE:
        raise NumberTooHigh("Sorry! I don't want to evaluate {0} >> {1}".format(a, b))
    return a >> b


def safe_lshift(a, b):  # pylint: disable=invalid-name
    """lshift, but with input limits"""
    if abs(b) > MAX_SHIFT or abs(a) > MAX_SHIFT_BASE:
        raise NumberTooHigh("Sorry! I don't want to evaluate {0} << {1}".format(a, b))
    return a << b


########################################
# Defaults for the evaluator:

DEFAULT_OPERATORS = {
    ast.Add: safe_add,
    ast.Sub: op.sub,
    ast.Mult: safe_mult,
    ast.Div: op.truediv,
    ast.FloorDiv: op.floordiv,
    ast.RShift: safe_rshift,
    ast.LShift: safe_lshift,
    ast.Pow: safe_power,
    ast.Mod: op.mod,
    ast.Eq: op.eq,
    ast.NotEq: op.ne,
    ast.Gt: op.gt,
    ast.Lt: op.lt,
    ast.GtE: op.ge,
    ast.LtE: op.le,
    ast.Not: op.not_,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
    ast.BitXor: op.xor,
    ast.BitOr: op.or_,
    ast.BitAnd: op.and_,
    ast.Invert: op.invert,
    ast.In: lambda x, y: op.contains(y, x),
    ast.NotIn: lambda x, y: not op.contains(y, x),
    ast.Is: lambda x, y: x is y,
    ast.IsNot: lambda x, y: x is not y,
}

DEFAULT_FUNCTIONS = {
    "rand": random,
    "randint": random_int,
    "int": int,
    "float": float,
    # pylint: disable=undefined-variable
    "str": str if PYTHON3 else unicode,  # type: ignore
}

DEFAULT_NAMES = {"True": True, "False": False, "None": None}

ATTR_INDEX_FALLBACK = True


########################################
# And the actual evaluator:


class SimpleEval(object):  # pylint: disable=too-few-public-methods
    """A very simple expression parser.
    >>> s = SimpleEval()
    >>> s.eval("20 + 30 - ( 10 * 5)")
    0
    """

    expr = ""

    def __init__(self, operators=None, functions=None, names=None):
        """
        Create the evaluator instance.  Set up valid operators (+,-, etc)
        functions (add, random, get_val, whatever) and names."""

        if operators is None:
            operators = DEFAULT_OPERATORS.copy()
        if functions is None:
            functions = DEFAULT_FUNCTIONS.copy()
        if names is None:
            names = DEFAULT_NAMES.copy()

        self.operators = operators
        self.functions = functions
        self.names = names

        self.nodes = {
            ast.Expr: self._eval_expr,
            ast.Assign: self._eval_assign,
            ast.AugAssign: self._eval_aug_assign,
            ast.Import: self._eval_import,
            ast.Num: self._eval_num,
            ast.Str: self._eval_str,
            ast.Name: self._eval_name,
            ast.UnaryOp: self._eval_unaryop,
            ast.BinOp: self._eval_binop,
            ast.BoolOp: self._eval_boolop,
            ast.Compare: self._eval_compare,
            ast.IfExp: self._eval_ifexp,
            ast.Call: self._eval_call,
            ast.keyword: self._eval_keyword,
            ast.Subscript: self._eval_subscript,
            ast.Attribute: self._eval_attribute,
            ast.Index: self._eval_index,
            ast.Slice: self._eval_slice,
        }

        # py3k stuff:
        if hasattr(ast, "NameConstant"):
            self.nodes[ast.NameConstant] = self._eval_constant

        # py3.6, f-strings
        if hasattr(ast, "JoinedStr"):
            self.nodes[ast.JoinedStr] = self._eval_joinedstr  # f-string
            self.nodes[
                ast.FormattedValue
            ] = self._eval_formattedvalue  # formatted value in f-string

        # py3.8 uses ast.Constant instead of ast.Num, ast.Str, ast.NameConstant
        if hasattr(ast, "Constant"):
            self.nodes[ast.Constant] = self._eval_constant

        # Defaults:

        self.ATTR_INDEX_FALLBACK = ATTR_INDEX_FALLBACK

        # Check for forbidden functions:

        for f in self.functions.values():
            if f in DISALLOW_FUNCTIONS:
                raise FeatureNotAvailable("This function {} is a really bad idea.".format(f))

    def __del__(self):
        self.nodes = None

    @staticmethod
    def parse(expr):
        """parse an expression into a node tree"""

        parsed = ast.parse(expr.strip())

        if not parsed.body:
            raise InvalidExpression("Sorry, cannot evaluate empty string")
        if len(parsed.body) > 1:
            warnings.warn(
                "'{}' contains multiple expressions. Only the first will be used.".format(expr),
                MultipleExpressions,
            )
        return parsed.body[0]

    def eval(self, expr, previously_parsed=None):
        """evaluate an expresssion, using the operators, functions and
        names previously set up."""

        # set a copy of the expression aside, so we can give nice errors...
        self.expr = expr

        return self._eval(previously_parsed or self.parse(expr))

    def _eval(self, node):
        """The internal evaluator used on each node in the parsed tree."""

        try:
            handler = self.nodes[type(node)]
        except KeyError:
            raise FeatureNotAvailable(
                "Sorry, {0} is not available in this " "evaluator".format(type(node).__name__)
            )

        return handler(node)

    def _eval_expr(self, node):
        return self._eval(node.value)

    def _eval_assign(self, node):
        warnings.warn(
            "Assignment ({}) attempted, but this is ignored".format(self.expr), AssignmentAttempted
        )
        return self._eval(node.value)

    def _eval_aug_assign(self, node):
        warnings.warn(
            "Assignment ({}) attempted, but this is ignored".format(self.expr), AssignmentAttempted
        )
        return self._eval(node.value)

    @staticmethod
    def _eval_import(node):
        raise FeatureNotAvailable("Sorry, 'import' is not allowed.")

    @staticmethod
    def _eval_num(node):
        return node.n

    @staticmethod
    def _eval_str(node):
        if len(node.s) > MAX_STRING_LENGTH:
            raise IterableTooLong(
                "String Literal in statement is too long!"
                " ({0}, when {1} is max)".format(len(node.s), MAX_STRING_LENGTH)
            )
        return node.s

    @staticmethod
    def _eval_constant(node):
        if hasattr(node.value, "__len__") and len(node.value) > MAX_STRING_LENGTH:
            raise IterableTooLong(
                "Literal in statement is too long!"
                " ({0}, when {1} is max)".format(len(node.value), MAX_STRING_LENGTH)
            )
        return node.value

    def _eval_unaryop(self, node):
        try:
            operator = self.operators[type(node.op)]
        except KeyError:
            raise OperatorNotDefined(node.op, self.expr)
        return operator(self._eval(node.operand))

    def _eval_binop(self, node):
        try:
            operator = self.operators[type(node.op)]
        except KeyError:
            raise OperatorNotDefined(node.op, self.expr)
        return operator(self._eval(node.left), self._eval(node.right))

    def _eval_boolop(self, node):
        to_return = False
        if isinstance(node.op, ast.And):
            for value in node.values:
                to_return = self._eval(value)
                if not to_return:
                    break
        elif isinstance(node.op, ast.Or):
            for value in node.values:
                to_return = self._eval(value)
                if to_return:
                    break
        return to_return

    def _eval_compare(self, node):
        right = self._eval(node.left)
        to_return = True
        for operation, comp in zip(node.ops, node.comparators):
            if not to_return:
                break
            left = right
            right = self._eval(comp)
            to_return = self.operators[type(operation)](left, right)
        return to_return

    def _eval_ifexp(self, node):
        return self._eval(node.body) if self._eval(node.test) else self._eval(node.orelse)

    def _eval_call(self, node):
        if isinstance(node.func, ast.Attribute):
            func = self._eval(node.func)
        else:
            try:
                func = self.functions[node.func.id]
            except KeyError:
                raise FunctionNotDefined(node.func.id, self.expr)
            except AttributeError:
                raise FeatureNotAvailable("Lambda Functions not implemented")

            if func in DISALLOW_FUNCTIONS:
                raise FeatureNotAvailable("This function is forbidden")

        return func(
            *(self._eval(a) for a in node.args), **dict(self._eval(k) for k in node.keywords)
        )

    def _eval_keyword(self, node):
        return node.arg, self._eval(node.value)

    def _eval_name(self, node):
        try:
            # This happens at least for slicing
            # This is a safe thing to do because it is impossible
            # that there is a true exression assigning to none
            # (the compiler rejects it, so you can't even
            # pass that to ast.parse)
            if hasattr(self.names, "__getitem__"):
                return self.names[node.id]
            if callable(self.names):
                return self.names(node)
            raise InvalidExpression(
                'Trying to use name (variable) "{0}"'
                ' when no "names" defined for'
                " evaluator".format(node.id)
            )

        except KeyError:
            if node.id in self.functions:
                return self.functions[node.id]

            raise NameNotDefined(node.id, self.expr)

    def _eval_subscript(self, node):
        container = self._eval(node.value)
        key = self._eval(node.slice)
        # Currently if there's a KeyError, that gets raised straight up.
        # TODO: Should that be wrapped in an InvalidExpression?
        return container[key]

    def _eval_attribute(self, node):
        for prefix in DISALLOW_PREFIXES:
            if node.attr.startswith(prefix):
                raise FeatureNotAvailable(
                    "Sorry, access to __attributes "
                    " or func_ attributes is not available. "
                    "({0})".format(node.attr)
                )
        if node.attr in DISALLOW_METHODS:
            raise FeatureNotAvailable(
                "Sorry, this method is not available. " "({0})".format(node.attr)
            )
        # eval node
        node_evaluated = self._eval(node.value)

        # Maybe the base object is an actual object, not just a dict
        try:
            return getattr(node_evaluated, node.attr)
        except (AttributeError, TypeError):
            pass

        # TODO: is this a good idea?  Try and look for [x] if .x doesn't work?
        if self.ATTR_INDEX_FALLBACK:
            try:
                return node_evaluated[node.attr]
            except (KeyError, TypeError):
                pass

        # If it is neither, raise an exception
        raise AttributeDoesNotExist(node.attr, self.expr)

    def _eval_index(self, node):
        return self._eval(node.value)

    def _eval_slice(self, node):
        lower = upper = step = None
        if node.lower is not None:
            lower = self._eval(node.lower)
        if node.upper is not None:
            upper = self._eval(node.upper)
        if node.step is not None:
            step = self._eval(node.step)
        return slice(lower, upper, step)

    def _eval_joinedstr(self, node):
        length = 0
        evaluated_values = []
        for n in node.values:
            val = str(self._eval(n))
            if len(val) + length > MAX_STRING_LENGTH:
                raise IterableTooLong("Sorry, I will not evaluate something this long.")
            evaluated_values.append(val)
        return "".join(evaluated_values)

    def _eval_formattedvalue(self, node):
        if node.format_spec:
            fmt = "{:" + self._eval(node.format_spec) + "}"
            return fmt.format(self._eval(node.value))
        return self._eval(node.value)


class EvalWithCompoundTypes(SimpleEval):
    """
    SimpleEval with additional Compound Types, and their respective
    function editions. (list, tuple, dict, set).
    """

    _max_count = 0

    def __init__(self, operators=None, functions=None, names=None):
        super(EvalWithCompoundTypes, self).__init__(operators, functions, names)

        self.functions.update(list=list, tuple=tuple, dict=dict, set=set)

        self.nodes.update(
            {
                ast.Dict: self._eval_dict,
                ast.Tuple: self._eval_tuple,
                ast.List: self._eval_list,
                ast.Set: self._eval_set,
                ast.ListComp: self._eval_comprehension,
                ast.GeneratorExp: self._eval_comprehension,
            }
        )

    def eval(self, expr, previously_parsed=None):
        # reset _max_count for each eval run
        self._max_count = 0
        return super(EvalWithCompoundTypes, self).eval(expr, previously_parsed)

    def _eval_dict(self, node):
        result = {}

        for key, value in zip(node.keys, node.values):
            if PYTHON35 and key is None:
                # "{**x}" gets parsed as a key-value pair of (None, Name(x))
                result.update(self._eval(value))
            else:
                result[self._eval(key)] = self._eval(value)

        return result

    def _eval_list(self, node):
        result = []

        for item in node.elts:
            if PYTHON3 and isinstance(item, ast.Starred):
                result.extend(self._eval(item.value))
            else:
                result.append(self._eval(item))

        return result

    def _eval_tuple(self, node):
        return tuple(self._eval(x) for x in node.elts)

    def _eval_set(self, node):
        return set(self._eval(x) for x in node.elts)

    def _eval_comprehension(self, node):
        to_return = []

        extra_names = {}

        previous_name_evaller = self.nodes[ast.Name]

        def eval_names_extra(node):
            """
            Here we hide our extra scope for within this comprehension
            """
            if node.id in extra_names:
                return extra_names[node.id]
            return previous_name_evaller(node)

        self.nodes.update({ast.Name: eval_names_extra})

        def recurse_targets(target, value):
            """
                Recursively (enter, (into, (nested, name), unpacking)) = \
                             and, (assign, (values, to), each
            """
            if isinstance(target, ast.Name):
                extra_names[target.id] = value
            else:
                for t, v in zip(target.elts, value):
                    recurse_targets(t, v)

        def do_generator(gi=0):
            g = node.generators[gi]
            for i in self._eval(g.iter):
                self._max_count += 1

                if self._max_count > MAX_COMPREHENSION_LENGTH:
                    raise IterableTooLong("Comprehension generates too many elements")
                recurse_targets(g.target, i)
                if all(self._eval(iff) for iff in g.ifs):
                    if len(node.generators) > gi + 1:
                        do_generator(gi + 1)
                    else:
                        to_return.append(self._eval(node.elt))

        try:
            do_generator()
        finally:
            self.nodes.update({ast.Name: previous_name_evaller})

        return to_return


def simple_eval(expr, operators=None, functions=None, names=None):
    """Simply evaluate an expresssion"""
    s = SimpleEval(operators=operators, functions=functions, names=names)
    return s.eval(expr)
