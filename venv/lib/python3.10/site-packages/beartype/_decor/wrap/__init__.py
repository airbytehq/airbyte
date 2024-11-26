#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

# ....................{ TODO                              }....................
#FIXME: Major optimization: duplicate the signature of the decorated callable
#as the signature of our wrapper function. Why? Because doing so obviates the
#need to explicitly test whether each possible parameter was passed and how
#that parameter was passed (e.g., positional, keyword) as well as the need to
#localize "__beartype_args_len" and so on. In short, this is a massive win.
#Again, see the third-party "makefun" package, which purports to already do so.

#FIXME: Cray-cray optimization: don't crucify us here, folks, but eliminating
#the innermost call to the original callable in the generated wrapper may be
#technically feasible. It's probably a BadIdea™, but the idea goes like this:
#
#    # Source code for this callable as a possibly multiline string,
#    # dynamically parsed at runtime with hacky regular expressions from
#    # the physical file declaring this callable if any *OR* "None" otherwise
#    # (e.g., if this callable is defined dynamically or cannot be parsed from
#    # that file).
#    func_source = None
#
#    # Attempt to find the source code for this callable.
#    try:
#        func_source = inspect.getsource(func)
#    # If the inspect.getsource() function fails to do so, shrug.
#    except OSError:
#        pass
#
#    # If the source code for this callable cannot be found, fallback to
#    # simply calling this callable in the conventional way.
#    if func_source is None:
#       #FIXME: Do what we currently do here.
#    # Else, the source code for this callable was found. In this case,
#    # carefully embed this code into the code generated for this wrapper.
#    else:
#       #FIXME: Do something wild, crazy, and dangerous here.
#
#Extreme care will need to be taken, including:
#
#* Ensuring code is indented correctly.
#* Preserving the signature (especially with respect to passed parameters) of
#  the original callable in the wrapper. See the third-party "makefun" package,
#  which purports to already do so. So, this is mostly a solved problem --
#  albeit still non-trivial, as "beartype" will never have dependencies.
#* Don't bother reading any of this. Just skip to the synopsis below:
#  * Preventing local attributes defined by this wrapper as well as global
#    attributes imported into this wrapper's namespace from polluting the
#    namespace expected by the original callable. The former is trivial; simply
#    explicitly "del {attr_name1},...,{attr_nameN}" immediately before
#    embedding the source code for that callable. The latter is tricky; we'd
#    probably want to stop passing "globals()" to exec() below and instead pass
#    a much smaller list of attributes explicitly required by this wrapper.
#    Even then, though, there's probably no means of perfectly insulating the
#    original code from all wrapper-specific global attributes. Or:
#    * Perhaps this isn't an issue? After all, *ALL* locals and globals exposed
#      to decorated callables are now guaranteed to be "__bear"-prefixed. This
#      implies that searching the body of the decorated callable for the
#      substring "\b__bear" and then raising an exception if any such
#      substrings are found should suffice to prevent name collision.
#  * Rewriting return values and yielded values. Oh, boy. That's the killer,
#    honestly. Regular expression-based parsing only gets us so far. We could
#    try analyzing the AST for that code, but... yikes. Each "return" and
#    "yield" statement would need to be replaced by a beartype-specific
#    "return" or "yield" statement checking the types of the values to be
#    returned or
#    yielded. We can guarantee that that rapidly gets cray-cray, especially
#    when implementing non-trivial PEP 484-style type checking requiring
#    multiple Python statements and local variables and... yeah. Actually:
#    * Why *CAN'T* regex-based parsing suffice? Python's Backus-Naur form (BNF)
#      is almost certainly quite constrained. We'll have to check where exactly
#      "return" and "yield" statements are permissible, but we're fairly sure
#      they're permissible only after newlines followed by sufficient
#      indentation.
#    * Note that the objects produced by Python's standard "ast" *AND* "dis"
#      modules contain line number attributes yielding the line numbers on
#      which those syntactic object were parsed. Ergo, whichever of these is
#      the more efficient almost certainly the simplest (and possibly even)
#      fastest approach. Is this worth benchmarking? Perhaps we should simply
#      adopt the "ast" approach, as that's likely to be substantially more
#      robust *AND* generalize to the case of annotated local variables, where
#      naive regexes (and probably "dis" as well) fall down. Of course, "dis"
#      is likely to be *MUCH* more space- and time-performant than "ast".
#    * *SIGH.* Yes, absolutely use the standard "ast" module. Absolutely do
#      *NOT* use either hand-rolled regexes or the standard "dis" module. Why?
#      Because:
#      * The low-level internals of the "ast" module are implemented in C. That
#        means it's likely to be fast enough for our purposes.
#      * CPython *ALREADY* has to do all (or at least, enough) of the AST
#        analysis performed by the "ast" module. Since that cost has to be paid
#        anyway, we'd might as well avoid paying additional regex or "dis"
#        costs by reusing "ast" with @beartype. Oh, wait... No, that's not how
#        things work at all. You basically can't reverse-engineer an AST from a
#        callable code object. Since Python doesn't preserve the AST it
#        internally produces to generate byte-code for a callable on that
#        callable, we have no choice but to:
#        * Get the source for that callable (e.g., with dill.source.getsource()
#          or inspect.getsource()).
#        * Pass that source string to ast.parse(). Man, that sure blows chunks.
#      * So, ignore the prior point. The only additional meaningful point is
#        that, unlike the "dis" module, the "ast" module makes it trivial to:
#        * Transform the produced AST by injecting additional nodes (e.g.,
#          dynamically generated statements) into the AST.
#        * Compile that AST down into a code object.
#      Does any of the above help us? Maybe not. All we really need from "ast"
#      and "dis" are line numbers and the ability to crudely identify:
#      * "return" statements. "dis" trivially does this.
#      * "yield" statements. "dis" trivially does this.
#      * Local annotated variable assignments. "dis" *PROBABLY* does not
#        trivially do this. Indeed, it's not necessarily clear that "ast" does
#        this either. Actually, that's absolutely *NOT* true. "ast" appears to
#        trivially detect local annotated variable assignments, which is nice.
#       Hilariously, regexes *DO* trivially detect local annotated variable
#       assignments, because that's just a search for
#       r"\n\s*[a-zA-Z_][a-zA-Z0-9_]*\s*:". Like, seriously. That's by far the
#       easiest way to do that. Detecting "return" and "yield" statements is
#       similarly trivial (we think, anyway) with regexes.
#       *WAIT.* Regexes may vary well detect the *START* of a local annotated
#       variable assignment, but they clearly fail to detect the *END*, as that
#       requires context-free parsing. Welp. That's the death-knell for both
#       regexes and "dis", then. "ast" is it!
#
#In synopsis, don't bother reading the above. Just know that parsing "return"
#and "yield" statements as well as annotated local variable assignments
#unsurprisingly requires use of the standard "ast" module. Specifically:
#* Get the source for the decorated callable. Ideally, we'll want to do so by
#  implementing our own get_callable_source() utility getter inspired by the
#  third-party "dill" implementation at dill.source.getsource() rather than the
#  standard inspect.getsource().
#* Pass that source string to ast.parse(). Note that the following snippet
#  appears to be the most robust means of doing so, as it implicitly accounts
#  for encoding issues that we do *NOT* want to concern ourselves with:
#      import ast
#      import tokenize
#
#      def parse_file(filename):
#          with tokenize.open(filename) as f:
#              return ast.parse(f.read(), filename=filename)
#  Please cite the original source for this, which is this blog article:
#  https://julien.danjou.info/finding-definitions-from-a-source-file-and-a-line-number-in-python
#* Search the resulting AST for any nodes referencing an object name (e.g.,
#  variable, callable, class) prefixed by "__bear" and raise an exception on
#  the first such node to prevent name collision.
#* Munge that AST as required.
#* Compile that AST -- ideally directly into a callable (but possibly first
#  indirectly into a code object into then that directly into a callable).
#
#I suppose we could gradually roll out support by (in order):
#* Initially duplicating the signature of the decorated callable onto the
#  wrapper function. Since this is both a hard prerequisite for all subsequent
#  work *AND* yields tangible benefits in and of itself (e.g., for runtime
#  introspection), this is absolutely the first big ticket item here. Note that
#  several approaches exist here:
#  * Programmatically reconstruct this signature. This is almost certainly the
#    optimal technique.
#  * Use "ast" to find the line interval for the signature of the decorated
#    callable in its source file.
#  * Use "dis" to find the same.
#
#  Note that this is complicated by default values, which will need to be
#  propagated from the decorated callable onto the wrapper function. As we
#  recall, the "callable.__defaults__" dunder variable contains these defaults,
#  so that's probably trivial. Just copy that variable, right? Similarly, the
#  "callable.__annotations__" dunder variable should also be propagated.
#
#  Actually, just see the standard inspect._signature_from_function() function,
#  which implements the core callable signature parsing logic. Alternately, I
#  believe we'd previously found a third-party library or two whose sole reason
#  for existence was parsing and duplicating callable signatures, wasn't it?
#* Then optimizing callables annotated by either no return type hint *OR* a
#  deeply ignorable return hint, which reduces to a significantly simpler edge
#  case requiring *NO* "ast" use.
#* Then optimizing callables returning and yielding nothing by falling back to
#  the unoptimized approach for callables that do so.
#* Then optimizing callables terminating in a single "return" or "yield"
#  statement that *DIRECTLY* return a local or global variable. This is the
#  easy common case, as we can then immediately precede that statement with a
#  type-check on that variable.
#* Then optimizing callables terminating in a single "return" or "yield"
#  statement that return an arbitrary expression. If that expression is *NOT* a
#  local or global variable, we need to capture that expression into a new
#  local variable *BEFORE* type-checking that variable *BEFORE* returning that
#  variable. So it goes.
#* Then optimizing callables containing multiple such statements.
#
#Note lastly that the third-party "dill" package provides a
#dill.source.getsource() function with the same API as the stdlib
#inspect.getsource() function but augmented in various favourable ways. *shrug*
#
#Although this will probably never happen, it's still mildly fun to ponder.
#FIXME: Actually, this should probably happen -- but not necessarily for the
#reasons stipulated above. Don't get us wrong; optimizing away the additional
#stack frame by embedding the body of the decorated callable directly into the
#wrapper function wrapping that callable is a clever (albeit highly
#non-trivial) optimization.
#
#The *REAL* tangible benefit, however, is in type-checking annotated local
#variables. Currently, neither @beartype nor any other runtime type checker has
#the means to check annotated local variables: e.g.,
#    @beartype
#    def muh_func(muh_list: list[int]) -> int:
#        list_item: int = list[0]    # <- can't check this
#        return list_item
#
#The reason, of course, is that those variables and thus variable annotations
#are effectively "locked" behind the additional stack frame separating the
#decorated callable from its wrapper function. Integrating the former into the
#latter, however, trivially dissolves this barrier; indeed, since Python
#currently has no notion of a variable decorator and prohibits function return
#values from being assigned to as l-values, there is no pragmatic alternative.
#
#The idea here is that we could augment the body of the decorated callable when
#merged into its wrapper function as follows:
#* Iteratively search that body for local annotated variable declarations.
#* For each such declaration:
#  * Inject one or more statements after each such declaration type-checking
#    that variable against its annotation.
#
#The issue here then becomes: *WHERE* after each such declaration? This is a
#pertinent question, because we could type-check a variable immediately after
#its declaration, only to have a subsequent assignment to that variable later
#in the body of the decorated callable silently invalidate the prior
#type-check. Technically, since @beartype is an O(1) type-checker, we could
#re-perform type-checks after each assignment to an annotated local variable.
#But that seems a bit heavy-handed. Perhaps we should simply inject that code
#at the last possible moment -- which is to say, immediately *BEFORE* each
#"return" or "yield" statement in that callable. We have to inject code there
#anyway to type-check that "return" or "yield" statement, so we'd be hitting
#two birds with one beating stick to additionally type-check annotated local
#variables there as well.
#
#Note that the answer to where we type-check local variables has a profound
#impact on whether we adopt a regex- or "ast"-based solution. If we type-check
#everything before "return" or "yield" statements, regex suffices. If we check
#variables immediately after their declaration or assignment, however, only
#"ast" suffices. This is, of course, yet another point in favour of checking
#everything before "return" or "yield" statements, as regex is likely to be
#substantially faster and more portable (due to changes in "ast" design and
#implementation across Python versions) than the "ast"-based approach.
#
#For example, this regex should (in theory) suffice to detect all annotated
#local variable declarations in a callable: r"\n\s+[a-zA-Z_][a-zA-Z0-9_]*\s*:".
#Oh... wait. No. Even that doesn't generalize. Why? Literal triple-quoted
#strings, obviously. Welp. "ast" it is, then! No point in beating around that
#context-free bush then, is there? Consider using the third-party "astor"
#package if available, which purportedly improves upon the standard "ast"
#module in various ways and is internally leveraged by "pylint" to perform its
#magic. In any case, Relevant articles include:
#* "Static Modification of Python With Python: The AST Module", a well-written
#  introduction to the topic:
#  https://dzone.com/articles/static-modification-python
#
#Note that we have two significant high-level choices here:
#* Use the "ast" module just to obtain line number intervals for the desired
#  statements. Note that the existence of the rarely used optional statement
#  terminator ";" makes this less trivial than desired. We can't simply assume
#  that statements begin and end on newlines, for example. Instead, we need to
#  employ either the Python >= 3.8-specific ast.get_source_segment() function
#  *OR* the Python >= 3.8-specific "end_lineno" and "end_col_offset" attributes
#  of AST nodes. In either case, Python >= 3.8 will absolutely be required.
#* Use the "ast" to dynamically transform the AST itself. This is considerably
#  less trivial *AND* invites significant issues. Sanely transforming the AST
#  would probably require refactoring our entire workflow to generate new
#  low-level AST nodes rather than new high-level Python code. Issues include:
#  * Efficiency. "ast" is both space- and time-inefficient, given both the
#    large number of objects it creates *AND* the inherent inefficiency of
#    binary trees as O(n log n) structures.
#  * Portably. "ast" commonly changes in significant ways between major Python
#    versions, casting doubts on our ability to reasonably port code
#    transforming the AST between major Python versions, which is unacceptable.
#
#Actually, we'll probably end up combining the two approaches above. We
#definitely *WILL* want to apply trivial AST transformations, including:
#* For "return" and "yield" statements, we'll need to split the AST nodes
#  representing those statements into at least three nodes plus a few new ones:
#  * The AST node representing each "return" and "yield" statement should be
#    transformed into a node instead localizing that statement's expression
#    into a new local variable named "__beartype_pith_0".
#  * Adding a new AST node returning or yielding the value of that variable.
#
#We can't reasonably do that transformation by any other means. Note that this
#then requires calling the Python >= 3.9-specific ast.unparse() function to
#losslessly generate source code from that transformed tree, which we then
#split into lines and inject our desired code after the desired line number
#corresponding to each shifted "return" and "yield" statement.
#
#After performing that hopefully simple transform, we then get the line number
#of the new AST node returning or yielding the value of that variable and then
#manually inject our code type-checking "__beartype_pith_0" there. Phew!
#
#Alternately, rather than ast.unparse() AST back into source code, we might
#instead try injecting AST nodes that we auto-generate by:
#* Passing our code type-checking the current "return" or "yield" statement to
#  the ast.parse() function.
#* Inject the target sub-AST returned by that call into the desired node of
#  the source full AST of the decorated callable. Note that this will probably
#  require prefixing the body of the decorated callable with our parameter
#  type-checking code *BEFORE* parsing that body with ast.parse(), to ensure
#  that references in our code type-checking the current "return" or "yield"
#  statement are properly resolved when merged back into the full AST.
#FIXME: Lastly, note that the above is likely to make beartype's
#decoration-time cost prohibitive under CPython, regardless of the call-time
#improvements due to stack frame compaction. Ergo, we may want to adopt the
#following defaults:
#* Under PyPy, *ENABLE* AST modification by default.
#* Under all other interpreters (especially including CPython), *DISABLE* AST
#  modification by default.
#
#Naturally, profile this to decide what we should do. To facilitate choice,
#we'll need to refactor the @beartype decorator to support a new optional
#"is_ast" parameter defaulting to something resembling these defaults. When
#this parameter is false, @beartype defaults to the current approach; else,
#@beartype modifies the AST of decorated callables as above.
#FIXME: *AH HA!* We just realized that the prior AST approach can be
#significantly optimized to a degree that might make this reasonably tractable
#under CPython as well. How? As follows (in order):
#* Dynamically synthesize the *PRELIMINARY* body of the wrapper function from
#  (in order):
#  * Code declaring the signature of the wrapper function. Note that we
#    *SHOULD* (in theory) be able to trivially extract this *WITHOUT* needing
#    to programmatically generate this ourselves this by performing a
#    preliminary walk over the AST of the decorated callable for the node(s)
#    responsible for declaring that callable's signature. Hopefully trivial.
#    Why? Because AST nodes provide line number ranges, which leads directly to
#    trivial extraction of callable signatures. That said... we probably
#    already need to programmatically generate signatures ourselves for the
#    common edge case in which the decorated callable is *NOT* annotated by a
#    return type hint. So, who knows!
#  * Code typing-checking all parameters, as above.
#  * Code typing-checking the "return" value. Don't worry about "yield"
#    statements for now. *YES,* we are intentionally type-checking the "return"
#    early in the body of the wrapper function. Why? So that we can have the
#    "ast" module generate a full AST tree containing a node performing that
#    type-check. Of course, that node will *NOT* be in the correct node
#    position. But that's fine. A subsequent step will shift that node to its
#    desired final position in the AST. This code should resemble:
#        __beartype_pith_0 = True
#        if ({code_checking_beartype_pith_0_value_here}):
#            raise {code_raising_beartype_pith_0_exception_here}
#    This is, of course, valid code that should generate valid AST nodes.
#  * The body of the decorated callable.
#* Parse that preliminary body of the wrapper function through the ast.parse()
#  function, producing an AST.
#* Transform that AST as follows:
#  * Iteratively walk that AST until finding a node assigning "True" to
#    "__beartype_pith_0". This shouldn't be troublesome.
#  * Extract both that node and the subsequent node subtree consisting of the
#    type-check and exception raising out of their current position in the AST.
#    Naturally, save these two nodes for subsequent reinsertion back into the
#    AST at a different position.
#  * Iteratively walk the remainder of the AST until finding a node performing
#    a return.
#  * Inject the two previously extracted nodes into that node position.
#  * Repeat until all "return" statements have been transformed.
#  * Voila!
#* Compile that AST directly into a code object by calling the ast.compile()
#  function.
#* Evaluate that code object by calling either the exec() or eval() builtin to
#  produce the actual wrapper function.
#
#Note that there is a significant annoyance associated with AST
#transformations: *LINE NUMBERS.* Specifically, the ast.compile() function
#called above absolutely requires that line numbers be coherent (i.e.,
#monotonically increase). To ensure this, we'll need to "fix up" line numbers
#for basically *ALL* nodes following those representing the code
#typing-checking all parameters (whose line numbers require no modification).
#This is annoying but inexpensive, given that we have to walk all nodes anyway.
#Note that the "ast" modules provides functions for repairing line numbers as
#well (e.g., ast.increment_lineno()), but that those functions are almost
#certainly inefficient and inapplicable for us.
#
#Note that the ast.copy_location() function appears to already do a *BIT* of
#what we need. Since we need cutting instead of copying, however, we'll
#probably just want to use that function's implementation as inspiration rather
#than directly calling that function.
#
#And... don't get us wrong. This is absolutely still going to be expensive. But
#the fact that we can flow directly from:
#   decorated callable -> source code -> AST -> code object -> wrapper func
#...does imply that this should be considerable faster than previously thought.
#FIXME: We just realized that there's a significant optimization here that
#renders stack frame reduction unconditionally worthwhile across all Python
#interpreters and versions in a simple common case: callables annotated either
#with no return type hints *OR* deeply ignorable type hints. Why? Because we
#can trivially eliminate the additional stack frame in this edge case by
#unconditionally prefixing the body of the decorated callable by (in order):
#
#1. Code type-checking parameters passed to that callable.
#2. Code deleting *ALL* beartype-specific "__bear"-prefixed locals and globals
#   referenced by the code type-checking those parameters. This is essential,
#   as it implies that we then no longer need to iteratively search the body of
#   the decorated callable for local variables with conflicting names, which
#   due to strings we can't reliably do without "ast"- or "dis"-style parsing.
#
#Note this edge case only applies to callables:
#* Whose return hint is either:
#  * Unspecified.
#  * Deeply ignorable.
#  * "None", implying this callable to return nothing. Callables explicitly
#    returning a "None" value should instead be annotated with a return hint of
#    "beartype.cave.NoneType"; this edge case would *NOT* apply to those.
#* *DIRECTLY* decorated by @beartype: e.g.,
#      @beartype
#      def muh_func(): pass
#  This edge case does *NOT* apply to callables directly decorated by another
#  decorator first, as in that case the above procedure would erroneously
#  discard the dynamic decoration of that other decorator: e.g.,
#      @beartype
#      @other_decorator
#      def wat_func(): pass
#* *NOT* implicitly transformed by one or more other import hooks. If any other
#  import hooks are in effect, this edge case does *NOT* apply, as in that case
#  the above procedure could again erroneously discard the dynamic
#  transformations applied by those other import hooks.
#FIXME: *GENERALIZATION:* All of the above would seem to pertain to a
#prospective higher-level package, which has yet to be officially named but
#which we are simply referring to as "beartypecache" for now. "beartypecache"
#has one dependency: unsurprisingly, this is "beartype". The principal goal of
#"beartypecache" is *NOT* to perform AST translations as detailed above,
#although that certainly is a laudable secondary goal.
#
#The principal goal of "beartypecache" is, as the name suggests, to cache
#wrapper functions dynamically generated by the @beartype decorator across
#Python processes. This goal succinctly ties in to the above AST transform
#concepts, because the *ONLY* sane means of performing these transforms (even
#under PyPy and similarly fast Python environments) is to cache the results of
#these transformations across Python processes.
#
#The underlying idea here is that the @beartype decorator only needs to be
#applied once to each version of a callable. If that callable has not changed
#since the last application of @beartype to that decorator (or since @beartype
#itself has changed, obviously), then the previously cached application of
#@beartype to the current version of that callable suffices. Naturally, of
#course, there exists *NO* efficient means of deciding when a callable has
#changed over multiple Python invocations. There does, however, exist an
#efficient means of deciding when an on-disk module defining standard callables
#has changed: the "__pycache__" directory formalized by "PEP 3147 -- PYC
#Repository Directories" at:
#    https://www.python.org/dev/peps/pep-3147
#
#Ergo, we soften the above idea to the following: "The @beartype decorator only
#needs to be applied once to each callable defined by each version of a
#module." If this sounds like import hooks, you would not be wrong. Sadly,
#there currently exists no public API in the stdlib for generically applying
#AST transformations via import hooks. But all is not lost, since we'll simply
#do it ourselves. In fact, unsurprisingly, this is a sufficiently useful
#concept that it's already been done by a number of third-party projects -- the
#most significant of which is "MacroPy3":
#    https://github.com/lihaoyi/macropy
#
#The "MacroPy3" synopsis reads:
#    "MacroPy provides a mechanism for user-defined functions (macros) to
#    perform transformations on the abstract syntax tree (AST) of a Python
#    program at import time."
#
#...which is exactly what we need. We certainly are *NOT* going to depend upon
#"MacroPy3" as a mandatory dependency, however. Like "beartype" before it,
#"beartypecache" should ideally only depend upon "beartype" as a mandatory
#dependency. Ideology aside, however, there exists a more significant reason:
#"beartypecache" is intended to be brutally fast. That's what the "cache"
#means. "MacroPy3" is undoubtedly slow by compare to a highly micro-optimized
#variant of that package, because no in the Python world cares about
#efficiency -- perhaps justifiably, but perhaps not. Moreover, generalization
#itself incurs space and time efficiency costs. We can eliminate those costs by
#developing our own internal, private, ad-hoc AST-transform-on-import-hook
#implementation micro-optimized for our specific use case.
#
#Amusingly, even the abandoned prominently references "MacroPy3":
#    The MacroPy project uses an import hook: it adds its own module finder in
#    sys.meta_path to hook its AST transformer.
#
#Note that "sys.meta_path" is *NOT* necessarily the optimum approach for
#"beartypecache". Since the @beartype decorator can only, by definition, be
#applied to third-party user-defined modules, "sys.meta_path" is might or might
#not be overkill for us, because "sys.meta_path" even applies to builtin
#stdlib modules. In any case, what we principally care about is the capacity to
#directly feed low-level *CODE OBJECTS* (rather than high-level *SOURCE CODE*)
#from our AST transformations into some sort of import hook machinery.
#
#Note this relevant StackOverflow answer:
#    https://stackoverflow.com/a/43573798/2809027
#The synopsis of that answer reads:
#    You will also need to examine if you want to use a MetaPathFinder or a
#    PathEntryFinder as the system to invoke them is different. That is, the
#    meta path finder goes first and can override builtin modules, whereas the
#    path entry finder works specifically for modules found on sys.path.
#That answer then goes on to succinctly define example implementations of both,
#which is ludicrously helpful. Again, we should adopt whichever allows us to
#most efficiently generate low-level *CODE OBJECTS* from AST transformations.
#
#Note that the public importlib.util.source_from_cache(path) function trivially
#enables us to obtain the absolute filename of the previously cached byte code
#file if any from the absolute filename of any arbitrary Python module. That's
#nice. Additionally, note this preamble to PEP 3147:
#
#    Byte code files [in "__pycache__" directories] contain two 32-bit
#    big-endian numbers followed by the marshaled code object. The 32-bit
#    numbers represent a magic number and a timestamp. The magic number changes
#    whenever Python changes the byte code format, e.g. by adding new byte
#    codes to its virtual machine. This ensures that pyc files built for
#    previous versions of the VM won't cause problems. The timestamp is used to
#    make sure that the pyc file match the py file that was used to create it.
#    When either the magic number or timestamp do not match, the py file is
#    recompiled and a new pyc file is written.
#
#Presumably, there exists some efficient programmatic means of deciding from
#pure Python whether "the magic number or timestamp do not match" for the byte
#code file cached for an arbitrary module.
#
#We're almost there. We then need some efficient means of deciding whether an
#arbitrary byte code file has been instrumented by "beartypecache" yet.
#That's... a much tougher nut to crack. We can think of two possible approaches
#here, both equally valid but one probably easier to implement than the other.
#For each byte code file cached in a "__pycache__" directory, the
#"beartypecache" package should either:
#* The easiest way *BY FAR* is probably to just emit one 0-byte
#  "beartypecache"-specific file named
#  "__pycache__/{module_name}.{python_name}.beartypecache" or something.
#  There's *NO* way any other package is writing that sort of file, so filename
#  collisions should in theory be infeasible. Given such a file, the "mtime" of
#  this file should coincide with that of the source module from which this
#  file is generated. Indeed, this approach suggests we don't even need to
#  extract the magic number and timestamp from the byte code file. Nice! So,
#  this is the way... probably.
#* The harder way *BY FAR* is probably to suffix the contents of this file by a
#  superfluous byte code statement specific to "beartypecache", effectively the
#  equivalent of:
#      __beartypecache_is_cached = True
#  That's more-or-less a noop and more-or-less trivially generated during our
#  AST transformation of this source module from an import hook. Given that,
#  we'd then just to need to compare the end of this file with the expected
#  byte sequence. This *DOES* entail some I/O overhead and considerably more
#  complexity than the prior approach, however.
#
#In any case, the above then enables us to efficiently cache @beartype
#decorations and AST transformations across an entire codebase as follows:
#
#* The root "__init__.py" module of the top-level package for downstream
#  third-party consumers should contain the following import:
#      import beartypecache.all
#  As a side effect, the "beartypecache.all" submodule then installs an import
#  hook globally decorating all callables across all subsequently imported
#  modules with @beartype as well as applying AST transformations. This is the
#  default approach. Of course, subsequent revisions could then provide some
#  degree of configurability via different submodules or subpackages.
#* This "beartypecache.all" import hook then confines itself to each
#  user-defined submodule *OF THE CALLING PACKAGE THAT IMPORTED*
#  "beartypecache.all". This is critical. We can't simply globally apply the
#  "beartypecache.all" import hook to *EVERYTHING*, because many callables will
#  neither be intended nor able to support decoration by @beartype, which has
#  rather firm views on PEP-compliant type hints and so on.
#* For each user-defined submodule of the calling package, this
#  "beartypecache.all" import hook then performs the following:
#  * Decide whether the previously cached byte code file for this submodule is
#    still synchronized with this submodule and has been previously
#    instrumented by "beartypecache", using one of the above approaches.
#  * If so, avoid uselessly re-instrumenting this file.
#  * Else, instrument this file as detailed above. As a first draft
#    implementation, "beartypecache" should simply:
#    * Replace the name of each function and method defined in this source
#      submodule by "__beartype_wrapped_{func_name}". Note this will require a
#      trivial sort of AST instrumentation. We can't avoid that.
#    * Define the replacement wrapper function with the name "{func_name}",
#      thus replacing the original callable with our decorated callable.
#    This draft implementation efficiently caches @beartype decorations across
#    the entire codebase, thus serving as a pragmatically useful demonstration
#    of the underlying concept.
#
#All in all, this requires funding. Technically feasible, but cray-cray.
