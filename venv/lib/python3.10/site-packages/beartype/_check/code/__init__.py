#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

# ....................{ TODO                               }....................
#FIXME: [SPEED] There exists a significant optimization that we *ABSOLUTELY*
#should implement. Currently, the "hints_meta" data structure is represented as
#a FixedList of size j, each item of which is a k-length tuple. If you briefly
#consider it, however, that structure could equivalently be represented as a
#FixedList of size j * k, where we simply store the items previously stored in
#each k-length tuple directly in that FixedList itself.
#
#Iterating forward and backward by single hints over that FixedList is still
#trivial. Rather than incrementing or decrementing an index by 1, we instead
#increment or decrement an index by k.
#
#The resulting structure is guaranteed to be considerably more space-efficient,
#due to being both contiguous in memory and requiring only a single object
#(and thus object dictionary) to maintain. Cue painless forehead slap.

#FIXME: [PEP] Add support for Python 3.10-specific PEPs and thus:
#* PEP 612-compliance. Since we don't currently support callable annotations,
#  we probably can't extend that non-existent support to PEP 612. Nonetheless,
#  we *ABSOLUTELY* should ensure that we do *NOT* raise exceptions when passed
#  the two new "typing" singletons introduced by this:
#  * "typing.ParamSpec", documented at:
#    https://docs.python.org/3.10/library/typing.html#typing.ParamSpec
#  * "typing.Concatenate", documented at:
#    https://docs.python.org/3.10/library/typing.html#typing.Concatenate
#  Ideally, we should simply ignore these singletons for now in a similar
#  manner to how we currently ignore type variables. After all, these
#  singletons are actually a new unique category of callable-specific type
#  variables. See also:
#  https://www.python.org/dev/peps/pep-0612
#* PEP 647-compliance. PEP 647 introduces a silly new subscriptable
#  "typing.TypeGuard" attribute. With respect to runtime type-checking, *ALL*
#  "typing.TypeGuard" subscriptions unconditionally reduce to "bool": e.g.,
#      from typing import TypeGuard, Union
#
#      # This...
#      def muh_func(muh_param: object) -> TypeGuard[str]:
#          return isinstance(muh_param, str)  # <-- gods help us
#
#      # This conveys the exact same runtime semantics as this.
#      def muh_func(muh_param: object) -> bool:
#          return isinstance(muh_param, str)  # <-- gods help us
#  Lastly, note that (much like "typing.NoReturn") "typing.TypeGuard"
#  subscriptions are *ONLY* usable as return annotations. Raise exceptions, yo.

#FIXME: [O(n)] Ah-ha! We now know how to implement O(log n) and O(n)
#type-checking in a scaleable manner that preserves @beartype's strong
#performance guarantees. How? With a timed deadline cutoff. Specifically:
#* Define a new "BeartypeConf.check_time_max_multiplier" instance variable,
#  which we've already conveniently documented.
#* Note this critical formula in the documentation for that variable (with the
#  equality flipped so as to express the condition under which @beartype
#  continues to perform type-checks):
#      b * check_time_max_multiplier < T
#
#  Naturally, real life isn't quite that convenient. We don't actually have
#  either "b" or "T". We need to dynamically compute them on each check. What we
#  *DO* have is:
#  * "B", the total time consumed by all *PRIOR* @beartype type-checks.
#  * "t", the current time.
#  * "s", the initial time at which the current round of @beartype type-checks
#    was started (e.g., for the current call to a @beartype-decorated callable).
#  * "Z", the initial time at which the active Python interpreter was started.
#
#  For convenience, additionally let:
#  * "K" be "check_time_max_multiplier" for readability.
#
#  Note that "t - s" yields the total time consumed by the *CURRENT* round of
#  @beartype type-checks. Ergo, "B + t - s" yields the total time consumed by
#  *ALL* @beartype type-checks. Given that, "b" and "T" can both then be
#  expressed in terms of these known quantities:
#      b = B + t - s
#      T =     t - Z
#
#  Then the above formula expands to:
#      (B + t - s) * K < t - Z     (4 total arithmetic operations)
#
#  Note that "t" *MUST* be localized as a local instance variable (e.g., as
#  "time_curr = time()) to avoid erroneous recomputation of that time. Also, "K"
#  and "Z" are constants. Ideally, we would be able to simplify away some of
#  this. Superficially, simplification yields *NO* significant joys:
#      Bk + Kt - Ks - t + Z < 0
#      Bk + Z + t(K - 1) < Ks      (6 total arithmetic operations)
#
#  However, "K - 1" is clearly also a constant. Let "L = K - 1". Then:
#      KB + Z + Lt < Ks            (5 total arithmetic operations)
#      KB - Ks + Z + Lt < 0
#      K(B - s) + Lt < -Z          (5 total arithmetic operations)
#
#  Ah-ha! But "-Z" is also a constant. Let "Y = -Z". Then we have:
#      K(B - s) + Lt < Y           (4 total arithmetic operations)
#
#  This is considerably better. Since "t" only appears once, we no longer need
#  to localize the result of calling the time() function and can instead simply
#  embed that call directly -- a significant savings in both time and code
#  complexity.
#
#  Can we do better? Possibly. Note that "s ~= t" for most intents and purposes.
#  In particular, "s - Z ~= t - Z" (with respect to orders of magnitude, which
#  is all the right side of that equation is attempting to capture, anyway).
#  We can then resimplify as follows:
#      (B + t - s) * K < s - Z     (4 total arithmetic operations)
#      KB + Kt - Ks - s < -Z
#      KB + Kt - Ks - s < -Z
#      K(B + t) - s(K + 1) < Y
#      K(B + t) - Ls < Y           (4 total arithmetic operations)
#
#  Amusingly, that fails to help (and in fact reduces accuracy). Gah! The best
#  we can do from here is to eliminate the need for "Y" from above as follows:
#      K(B - s) + Lt < -Z          (5 total arithmetic operations)
#      K(B - s) < -Lt - Z
#      K(B - s) < -(Lt + Z)
#      -K(B - s) > Lt + Z
#      K(s - B) > Lt + Z           (4 total arithmetic operations)
#      K(s - B) - Lt > Z           (4 total arithmetic operations)
#
#  Furthermore, note that:
#  * "s" is internally localized at the start of the body of each
#    @beartype-decorated callable.
#  * "t" is simply a call to the time() function.
#  * "K" and "L = K - 1" don't actually need to be passed anywhere. They're
#    *NOT* variables; they're just hard-coded in at code generation time.
#  * "B and Z", on the other hand, *DO* need to passed to each
#    @beartype-decorated callable under the O(n) strategy.
#  * Moreover, "B" *MUST* be updated by each @beartype-decorated callable under
#    the O(n) strategy.
#
#  Ah-ha! With respect to each call to a @beartype-decorated callable under the
#  O(n) strategy, the quantity "K(s - B)" is actually a constant. Since "Z" is
#  also a constant, we simply localize these two constants at the start of the
#  body of each such callable into a new constant "J = K(s - B) - Z". This then
#  yields:
#      K(s - B) - Lt > Z           (4 total arithmetic operations)
#      K(s - B) - Z > Lt
#      J > Lt
#      Lt < J                      (1 total arithmetic operation)
#
#  And... that's all she wrote, folks. While that condition holds, @beartype
#  continues performing O(n) type-checks. It should be noted that this
#  simplified conditional trivially follows from only a few steps of the
#  original conditional like so:
#      (B + t - s) * K < t - Z
#      KB + Kt - Ks < t - Z
#      Kt - t < Ks - KB - Z
#      t(K - 1) < K(s - B) - Z
#* Altogether, the above implies that each @beartype-decorated callable under
#  the O(n) strategy should be passed a new hidden "__beartype_times" parameter.
#  This parameter is a 2-list "(process_time_start, beartype_time_total)",
#  where:
#  * "process_time_start" is simply "Z".
#  * "beartype_time_total" is simply "B".
#
#  This 2-list is a global list exposed to each @beartype-decorated callable via
#  this "__beartype_times" parameter. Declare this global list in a separate
#  submodule -- say, a new "exprtime" submodule -- as follows:
#      from time import monotonic
#
#      CHECK_TIMES = [monotonic(), 0.0]
#      '''
#      **Type-checking wall-clock time accumulator** (i.e., list whose items
#      allow :mod:`beartype`-generated type-checkers under non-constant
#      strategies like :attr:`beartype.BeartypeStrategy.On` to record how much
#      time the active Python process has devoted to :mod:`beartype`, enabling
#      :mod:`beartype` to prematurely halt type-checking when those
#      type-checkers exceed scheduled deadlines).
#
#      Specifically, this global is a 2-list
#      ``(process_time_start, beartype_time_total)``, where:
#
#      * ``process_time_start`` is the initial time at which the active Python
#        process was started, denominated in fractional seconds.
#      * ``beartype_time_total`` is the total time consumed by all *prior*
#        :mod:`beartype`-generated type-checks, denominated in fractional
#        seconds.
#      '''
#* Now, note the naive implementation of an O(n) type-check for a callable
#  accepting a parameter annotated by the type hint "list[str]":
#      @beartype(conf=BeartypeConf(strategy=BeartypeStrategy.On))
#      def muh_callable(muh_param: list[str]) -> None:
#          ...
#
#          if not (
#              isinstance(muh_param, list) and
#              all(isinstance(muh_item, str) for muh_item in list)
#          ):
#              raise get_beartype_violation(...)
#          ...
#
#  Trivial. Now, note the non-naive implementation of the same O(n) type-check
#  respecting the "check_time_max_multiplier" configuration setting:
#      from beartype._check._expr.exprtime import CHECK_TIMES
#      from time import monotonic
#
#      @beartype(conf=BeartypeConf(strategy=BeartypeStrategy.On))
#      def muh_callable(
#          muh_param: list[str],
#          __beartype_check_times = CHECK_TIMES,
#          __beartype_get_time_monotonic = monotonic,
#      ) -> None:
#          # Constant "J" in the inequality "Lt < J" governing @beartype's
#          # deadline scheduler for non-constant type-checking, denominated in
#          # fractional seconds.
#          CHECK_TIME_START = __beartype_get_time_monotonic()
#          CHECK_TIME_MAX = (
#              {check_time_max_multiplier}(
#                  CHECK_TIME_START - __beartype_check_times[1]
#              ) - __beartype_check_times[0]
#          )
#
#          ...
#
#          if not (
#              isinstance(muh_param, list) and
#              # For each item of this iterable...
#              all(
#                  (
#                      # If @beartype has yet to exceed its scheduled deadline
#                      # for non-constant type-checks *AND*...
#                      (
#                          {check_time_max_multiplier - 1} *
#                          __beartype_get_time_monotonic() < CHECK_TIME_MAX
#                      ) and
#                      isinstance(muh_item, str)
#                  )
#                  for muh_item in list
#              )
#          # *AND* @beartype has yet to exceed its scheduled deadline for
#          # non-constant type-checks...
#          ) and ({check_time_max_multiplier - 1}*monotonic() < CHECK_TIME_MAX):
#              raise get_beartype_violation(...)
#          # Else, this pith either satisfies this hint *OR* @beartype has
#          # exceeded its scheduled deadline for non-constant type-checks.
#
#          # Update the total time consumed by @beartype type-checks.
#          __beartype_check_times[1] += (
#              __beartype_get_time_monotonic() - CHECK_TIME_START)
#          ...
#
#Seriously trivial, everybody. \o/

#FIXME: [DFS] The "LRUDuffleCacheStrong" class designed below assumes that
#calculating the semantic height of a type hint (e.g., 3 for the complex hint
#Optional[int, dict[Union[bool, tuple[int, ...], Sequence[set]], list[str]])
#is largely trivial. It isn't -- at all. Computing that without a context-free
#recursion-esque algorithm of some sort is literally infeasible. We absolutely
#*MUST* get that height right, since we'll be exponentiating that height to
#estimate space consumption of arbitrary objects. Off-by-one errors are
#unacceptable when the difference between a height of 2 and a height of 3 means
#tens of thousands in additional estimated space consumption.
#
#So. How do we do this, then? *SIMPLE.* Okay, not simple -- but absolutely
#beneficial for a medley of unrelated pragmatic reasons and thus something we
#need to pursue anyway regardless of the above concerns.
#
#The solution is to make the breadth-first search (BFS) internally performed
#by the make_func_wrapper_code() function below more recursion-esque. We will
#*NOT* be refactoring that function to leverage:
#
#* Recursion rather than iteration for all of the obvious reasons.
#* A stack-like depth-first search (DFS) approach. While implementing a DFS
#  with iteration can technically be done, doing so imposes non-trivial
#  technical constraints because you then need to store interim results (which
#  in a proper recursive function would simply be local variables) as you
#  iteratively complete each non-leaf node. That's horrifying. So, we'll be
#  preserving our breadth-first search (BFS) approach. The reason why a BFS is
#  often avoided in the real world are space concerns: a BFS consumes
#  significantly more space than a comparable DFS, because:
#  * The BFS constructs the entire tree before operating on that tree.
#  * The DFS only constructs a vertical slice of the entire tree before
#    operating only on that slice.
#  In our case, however, space consumption of a BFS versus DFS is irrelevant.
#  Why? Because type hints *CANNOT* be deeply nested without raising recursion
#  limit errors from deep within the CPython interpreter, as we well know.
#  Ergo, a BFS will only consume slightly more temporary space than a DFS. This
#  means a "FixedList" of the same size trivially supports both.
#
#First, let's recap what we're currently doing:
#
#* In a single "while ...:" loop, we simultaneously construct the BFS tree
#  (stored in a "FixedList" of tuples) *AND* output results from that tree as
#  we are dynamically constructing it.
#
#The "simultaneously" is the problem there. We're disappointed we didn't
#realize it sooner, but our attempt to do *EVERYTHING* in a single pass is why
#we had such extraordinary difficulties correctly situating code generated by
#child type hints into the code generated for parent type hints. We
#circumvented the issue by repeatedly performing a global search-and-replace on
#the code being generated, which is horrifyingly inefficient *AND* error-prone.
#We should have known then that something was wrong. Sadly, we proceeded.
#
#Fortunately, this is the perfect moment to correct our wrongs -- before we
#proceed any deeper into a harmful path dependency. How? By splitting our
#current monolithic BFS algorithm into two disparate BFS phases -- each
#mirroring the behaviour of a recursive algorithm:
#
#1. In the first phase, a "while ...:" loop constructs the BFS tree by
#   beginning at the root hint, iteratively visiting all child hints, and
#   inserting metadata describing those hints into our "hints_meta" list as we
#   currently do. That's it. That's all. But that's enough. This construction
#   then gives us efficient random access over the entire type hinting
#   landscape, which then permits us to implement the next phase -- which does
#   the bulk of the work. To do so, we'll add additional metadata to our
#   current "hint_meta" tuple: e.g.,
#   * "_HINT_META_INDEX_CHILD_FIRST_INDEX", the 0-based index into the
#     "hints_meta" FixedList of the first child hint of the current hint if any
#     *OR* "None" otherwise. Since this is a BFS, that child hint could appear
#     at any 0-based index following the current hint; finding that child hint
#     during the second phase thus requires persisting the index of that hint.
#     Note that the corresponding index of the last child hint of the current
#     hint need *NOT* be stored, as adding the length of the argument list of
#     the current hint to the index of the first child hint trivially gives the
#     index of the last child hint.
#   * "_HINT_META_INDEX_CODE", the Python code snippet type-checking the
#     current hint to be generated by the second phase.
#   * "_HINT_META_INDEX_HEIGHT", the 1-based height of the current hint in this
#     BFS tree. Leaf nodes have a height of 1. All non-leaf nodes have a height
#     greater than 1. This height *CANNOT* be defined during the first phase
#     but *MUST* instead be deferred to the second phase.
#   * ...probably loads more stuff, but that's fine.
#2. In the second phase, another "while ...:" loop generates a Python code
#   snippet type-checking the root hint and all child hints visitable from that
#   hint in full by beginning *AT THE LAST CHILD HINT ADDED TO THE*
#   "hints_meta" FixedList, generating code type-checking that hint,
#   iteratively visiting all hints *IN THE REVERSE DIRECTION BACK UP THE TREE*,
#   and so on.
#
#That's insanely swag. It shames us that we only thought of it now. *sigh*
#FIXME: Note that this new approach will probably (hopefully only slightly)
#reduce decoration efficiency. This means that we should revert to optimizing
#the common case of PEP-noncompliant classes. Currently, we uselessly iterate
#over these classes with the same BFS below as we do PEP-compliant classes --
#which is extreme overkill. This will be trivial (albeit irksome) to revert,
#but it really is fairly crucial. *sigh*
#FIXME: Now that we actually have an audience (yay!), we *REALLY* need to avoid
#breaking anything. But implementing the above refactoring would absolutely
#break everything for an indeterminate period of time. So how do we do this?
#*SIMPLE*. We leave this submodule as is *UNTIL* our refactoring passes tests.
#In the meanwhile, we safely isolate our refactoring work to the following new
#submodules:
#* "_pephinttree.py", implementing the first phase detailed above.
#* "_pephintgene.py", implementing the second phase detailed above.
#
#To test, we locally change a simple "import" statement in the parent
#"_pepcode" submodule and then revert that import before committing. Rinse
#until tests pass, which will presumably take several weeks at least.
#FIXME: See additional commentary at this front-facing issue:
#    https://github.com/beartype/beartype/issues/31#issuecomment-799938621
#FIXME: Actually, *FORGET EVERYTHING ABOVE.* We actually do want to
#fundamentally refactor this iterative BFS into an iterative DFS. Why? Because
#we increasingly need to guard against both combinatorial explosion *AND*
#recursion. That's imperative -- and we basically *CANNOT* do that with the
#current naive BFS approach. Yes, implementing a DFS is somewhat more work. But
#it's *NOT* infeasible. It's very feasible. More importantly, it's necessary.
#Since @beartype should eventually handle recursive type hints, we'll need
#recursion guards anyway. Specifically:
#* Guarding against recursion would be trivial if we were actually using a
#  depth-first algorithm. While delving, you'd just maintain a local set of the
#  IDs of all type hints previously visited. You'd then avoid delving into
#  anything if the ID of that thing is already in that set. Likewise, after
#  delving into that thing, you'd then pop the ID of that thing off that set.
#* Likewise, handling combinatorial explosion would *ALSO* be trivial if we were
#  actually using a depth-first algorithm. By "combinatorial explosion," we are
#  referring to what happens if we try to type-check dataclass and
#  "typing.NamedTuple" instances that are *NOT* decorated by @beartype.
#  Type-checking those instances has to happen at @beartype call time, clearly.
#  There are actually two kinds of combinatorial explosion at play here:
#  * Combinatorial explosion while type-checking at @beartype call time. This is
#    avoidable by simply type-checking *EXACTLY ONE* random field of each
#    "NamedTuple" instance on each call. Simple. "NamedTuple" instances are
#    literally just tuples, so random access is trivial. (Type-checking random
#    fields of dataclass instances is less trivial but still feasible; just pass
#    a list whose values are dataclass field names as a private
#    @beartype-specific parameter to type-checking @beartype wrapper functions.
#    That list then effectively maps from 0-based indices to dataclass field
#    names. We then perform random access on that list to generate random field
#    names, which can then be accessed with reasonable efficiency.)
#  * Combinatorial explosion while generating type-checking code at @beartype
#    decoration time. This is the problem, folks. Why? Because we currently
#    employ a breadth-first search (BFS), which requires generating the entire
#    tree of all type hints to be visited. Currently, that's fine, because type
#    hints are typically compact; exhausting memory is unlikely. But as soon as
#    we start generating type-checking code for "NamedTuple" instances *NOT*
#    decorated by @beartype, we have to begin visiting *ALL* type hints
#    annotating *ALL* fields of those type hints by adding those hints to our
#    BFS tree. Suddenly, combinatorial explosion becomes a very real thing.
#
#The solution is to radically transform our existing BFS search into a DFS
#search. Again, this is something we would need to do eventually anyway to
#handle recursive type hints, because how can you guard against recursion in an
#iterative BFS anyway? And... anyway, DFS is simply the right approach. It's
#what we should have done all along, clearly. It's also non-trivial, which is
#why we didn't do it all along.
#
#For example, for each type hint visited by a DFS, we'll need to additionally
#record metadata like:
#* "_HINT_META_INDEX_ARGS_INDEX_NEXT", the 0-based index into the
#  "hint.__args__" tuple (listing all child type hints for the currently visited
#  type hint "hint") of the next child type hint of the associated parent type
#  hint to be visited. When "_HINT_META_INDEX_ARGS_INDEX_NEXT ==
#  len(hint.__args__)", the DFS has successfully visited all child type hints of
#  the currently visited type hint "hint" and should now iteratively recurse up
#  (rather than down) the DFS stack.
#* "_HINT_META_INDEX_CODE", the Python code snippet type-checking the currently
#  visited hint. This code snippet will be gradually filled in as child type
#  hints of the currently visited type hint are themselves visited. Indeed, this
#  implies that the currently visited parent type hint *MUST* always be able to
#  access the "_HINT_META_INDEX_CODE" entry of the most recently visited child
#  type hint of that parent -- which, in turn, implies that the entire
#  "hints_meta" FixedList of each child type hint must be temporarily preserved.
#  Specifically, when recursing up the DFS stack, each parent type hint will:
#  1. Access the "hints_meta" FixedList of its most recently visited child type
#     to fill in its own "_HINT_META_INDEX_CODE".
#  2. Pop that "hints_meta" FixedList of its most recently visited child type
#     hint off the DFS stack.
#
#Some type hints like unions will additionally require hint-specific entries in
#their "hints_meta" FixedList. The code for a union *CANNOT* be efficiently
#generated until *ALL* child type hints of that union have been. Although
#hint-specific entries could be appended to the "hints_meta" FixedList
#structure, doing so would rapidly increase the memory consumption of all other
#types of hints for no particularly good reason. Instead, a single new
#hint-specific entry should be added:
#* "_HINT_META_INDEX_DATA", an arbitrary object required by this kind of hint.
#  In the case of unions, this will be an instance of a dataclass resembling:
#      @dataclass
#      def _HintMetaDataUnion(object):
#          HINTS_CHILD_NONPEP = set()
#          '''
#          Set of all previously visited PEP-noncompliant child type hints
#          (e.g., isinstanceable classes) of this parent union type hint.
#          '''
#
#          HINTS_CHILD_PEP = set()
#          '''
#          Set of all previously visited PEP-compliant child type hints of this
#          parent union type hint.
#          '''
#
#   Naturally, "_HintMetaDataUnion" instances should be cached with the standard
#   acquire_object() and release_object() approach. *shrug*
#
#Oh! Wait. Nevermind. We don't actually need "_HINT_META_INDEX_DATA" or
#"_HintMetaDataUnion". It's true that we would need both if we needed to handle
#unions strictly with a classical DFS approach -- but there's *NO* pragmatic
#reason to do so. Instead, we'll just continue handling unions as we currently
#do: by iterating over child type hints of unions and separating them into
#PEP-compliant and PEP-noncompliant sets. So, basically a mini-BFS over unions
#*BEFORE* we then delve into their PEP-compliant child type hints in the
#standard DFS way. That's fine, because we're *NOT* purists here. Whatever is
#fastest and simplest (in that order) is what wins.
#
#Note that a DFS still needs to expensively interpolate code snippets into
#format templates. There's *NO* way around that; since dynamic code generation
#is what we've gotten ourselves into here, string munging is a necessary "good."
#FIXME: *OKAY.* It's time to contemplate the unthinkable, folks. Note that our
#existing make_check_expr() code generation function internally calls the
#_enqueue_hint_child() closure on each child. You should now be thinking: "Why
#didn't we simply implement this recursively?" Because that is what I am now
#thinking, people. Specifically, since we're *ALREADY* paying function call
#costs, there's little reason not to simply go full-blown recursion and
#implement this accordingly.
#
#Note that this is *NOT* to say that we should go FULL-FULL-BLOWN
#object-oriented via the DOOR API. That would impose substantial slowdown.
#Instead, rather, we should begin considering a family of low-level
#sign-specific functions that generate code for each sign category: e.g.,
#* _make_check_expr_union() for "HintSignUnion" hints.
#* _make_check_expr_sequence_1_arg() for "HintSignSequence" hints.
#* And so on.
#
#Then define a private dictionary mapping from signs to those functions. Viola!
#Misery has been substantially reduced.
#
#That said, the current approach still offers benefits. Since all state is
#centralized into a single function, sharing state between different
#code-generating "subfunctions" is trivial; they're just local variables. This
#suggests that we should initially:
#* Attempt to generalize the current single-function approach from BFS to DFS.
#* If that fails, do *NOT* hesitate to generalize to a multi-function recursive
#  approach. However we can implement this is how we must implement this.

#FIXME: Note that there exist four possible approaches to random item selection
#for arbitrary containers depending on container type. Either the actual pith
#object (in descending order of desirability):
#* Satisfies "collections.abc.Sequence" (*NOTE: NOT* "typing.Sequence", as we
#  don't particularly care how the pith is type-hinted for this purpose), in
#  which case the above approach trivially applies.
#* Else is *NOT* a one-shot container (e.g., generator and... are there any
#  other one-shot container types?) and is *NOT* slotted (i.e., has no
#  "__slots__" attribute), then generalize the mapping-specific
#  _get_dict_nonempty_random_key() approach delineated below.
#* Else is *NOT* a one-shot container (e.g., generator and... are there any
#  other one-shot container types?) but is slotted (i.e., has a "__slots__"
#  attribute), then the best we can do is the trivial O(1) approach by
#  calling "{hint_child_pith} := next({hint_curr_pith})" to unconditionally
#  check the first item of this container. What you goin' do? *shrug* (Note
#  that we could try getting around this with a global cache of weak references
#  to iterators mapped on object ID, but... ain't nobody got time or interest
#  for that. Also, prolly plenty dangerous.)
#* Else is a one-shot container, in which case *DO ABSOLUTELY NUTHIN'.*
#FIXME: We should ultimately make this user-configurable (e.g., as a global
#configuration setting). Some users might simply prefer to *ALWAYS* look up a
#fixed 0-based index (e.g., "0", "-1"). For the moment, however, the above
#probably makes the most sense as a reasonably general-purpose default.
#FIXME: [THIS-IS-BOSS] *AH-HA.* First, note that the above
#_get_dict_nonempty_random_key() concept, while clever, is largely useless. Why?
#Because *ALL* builtin C-based reiterables (e.g., dict, set) are slotted. We'd
#might as well just ignore that and leap straight to a general-purpose answer.
#
#Indeed, we've *FINALLY* realized how to genuinely perform iterative access to
#arbitrary non-sequence containers in an O(1) manner *WITHOUT* introducing
#memory leaks or requiring asynchronous background shenanigans. The core conceit
#is quite simple, really. Internally:
#
#* @beartype maintains two global dictionaries:
#  * A global "_REITERABLE_ID_TO_WEAKPROXY" dictionary mapping from the object
#    ID of each reiterable that has been previously type-checked by @beartype to
#    at least once to a strong reference to a "weakref.proxy" instance safely
#    proxying that reiterable.
#  * A global "_REITERABLE_ID_TO_ITER" dictionary mapping from the object ID of
#    each reiterable that has been previously type-checked by @beartype to
#    at least once to a strong reference to an iterator over that
#    "weakref.proxy" instance safely proxying that reiterable.
#
#  This approach substantially reduces the negative harms associated with memory
#  leaks -- although one worst-case memory leak *DOES* still remain. Notably,
#  since these proxies are themselves discrete objects, storing strong
#  references to both these proxies and these iterators could under worst-case
#  behaviour consume all available space. Ergo, this dictionary will need to be
#  efficiently maintained as a large (but still limited) LRU cache. Ideally, the
#  real-world size of this cache should be bound to a maximum of (say) 1MB space
#  consumption. Since only proxy shim objects and iterators over those objects
#  are stored (and we expect the size of these proxies and iterators to be quite
#  small), this cache *SHOULD* be able to support an exceedingly large number of
#  proxies before becoming full.
#
#  Since this dictionary is only leveraged for type-checking, thread
#  synchronization is irrelevant (although, of course, care should be taken to
#  ensure that this dictionary remains internally consistent regardless of
#  thread preemption).
#* @beartype provides a trivial _get_reiterable_item_next() getter for use in
#  dynamically generated type-checking code, which will then call that getter
#  rather than iter() on reiterables to retrieve an effectively random item from
#  those reiterables. Internally, this getter leverages the above global
#  dictionaries as follows:
#      # Note that this getter assumes the passed reiterable to be *NON-EMPTY.*
#      # It is the caller's responsibility to ensure that (e.g., by explicitly
#      # calling "len(reiterable)" or "bool(reiterable)" *BEFORE* calling this
#      # getter). Trivial, but worth noting. For efficiency, this getter
#      # intentionally does *NOT* explicitly validate that constraint.
#      def _get_reiterable_item_next(
#          reiterable: _BeartypeReiterableTypes) -> object:
#
#          #FIXME: Curiously, some C-based containers *DO* support weak
#          #references. Crucially, this includes sets, frozensets, arrays, and
#          #deques. Dicts, however, do *NOT*. Are dicts the only notable
#          #exceptions? Not quite. *ANY* user-defined reiterable defining
#          #"__slots__" that does *NOT* contain the string '__weakref__' also
#          #does *NOT* support weak references. In short, we can really only
#          #perform the following for a small subset of type hints: e.g.,
#          #* "typing.Deque".
#          #* "typing.FrozenSet".
#          #* "typing.Set".
#          #
#          #Aaaaaaand... we're pretty sure that's it. Three is better than
#          #nothing, of course. But... that's still not that great. We could try
#          #to dynamically test for weak-referenceability -- except we're pretty
#          #sure that that *CANNOT* be done efficiently in the general case.
#          #We'd need to either:
#          #* Call dir(), which dynamically creates and returns a new dict.
#          #  That's right out.
#          #* Access "__dict__" directly, which is only defined for pure-Python
#          #  instances. That attribute does *NOT* exist for C-based instances.
#          #
#          #Actually, the most efficient detection heuristic would probably be:
#          #* Define yet another global
#          #  "_REITERABLE_TYPE_TO_IS_WEAKREFFABLE" dictionary mapping from
#          #  reiterable types to boolean "True" only if those types can be
#          #  weakly referenced. This dictionary can be pre-initialized for
#          #  efficiency with the most common builtin C-based reiterable types
#          #  in a global context as follows:
#          #      _REITERABLE_TYPE_TO_IS_WEAKREFFABLE = {
#          #          DefaultDict: False,
#          #          dict: False,
#          #          deque: True,
#          #          frozenset: True,
#          #          set: True,
#          #      }
#          #  We don't bother LRU-bounding that. Size is irrelevant here.
#          #* Likewise, define yet another globl
#          #  "_REITERABLE_TYPE_TO_IS_LENGTHHINTED" dictionary mapping from
#          #  reiterable types to boolean "True" only if those types define
#          #  iterators defining semantically meaningful __length_hint__()
#          #  dunder methods. Since detecting that at runtime is infeasible, we
#          #  simply preallocate that to those we do know about:
#          #      _REITERABLE_TYPE_TO_IS_LENGTHHINTED = {
#          #          deque: True,  # <-- unsure if true, actually *shrug*
#          #          frozenset: True,
#          #          set: True,
#          #      }

#          #* Given that, we then efficiently detect weak-referenceability:
#
#          REITERABLE_TYPE = reiterable.__class__
#
#          #FIXME: Again, optimize ...get() method access, please.
#          reiterable_is_weakreffable = (
#              _REITERABLE_TYPE_TO_IS_WEAKREFFABLE.get(REITERABLE_TYPE))
#
#          if reiterable_is_weakreffable is None:
#              reiterable_dict = getattr(reiterable, '__dict__')
#              #FIXME: Alternately, we could try just taking a weak proxy
#              #of this reiterable and catching exceptions. Although
#              #slower, this caching operation only occurs once per type.
#              #For now, let's run with this faster heuristic.
#              if not reiterable_dict:
#                  reiterable_is_weakreffable = False
#              else:
#                  reiterable_slots = reiterable_dict.get('__slots__')
#                  reiterable_is_weakreffable = (
#                      reiterable_slots and
#                      '__weakref__' not in reiterable_slots
#                  )
#              _REITERABLE_TYPE_TO_IS_WEAKREFFABLE[REITERABLE_TYPE] = (
#                  reiterable_is_weakreffable)
#
#          # If this reiterable is a C-based container that does *NOT* support
#          # weak references, reduce to simply returning the first item of this
#          # reiterable.
#          if not reiterable_is_weakreffable:
#              return next(iter(reiterable))
#
#          REITERABLE_ID = id(reiterable)
#
#          #FIXME: Optimize by storing and calling a bound
#          #"_REITERABLE_ID_TO_ITER_get" method instead, please.
#          reiterable_iter = _REITERABLE_ID_TO_ITER.get(REITERABLE_ID)
#
#          if reiterable_iter:
#              #FIXME: Note that this can be conditionally optimized for
#              #iterators that define the PEP 424-compliant __length_hint__()
#              #dunder method -- which thankfully appears to be *ALL* iterators
#              #over C-based reiterables (e.g., dicts, sets). For these objects,
#              #__length_hint__() provides the number of remaining items in the
#              #iterator. Ergo, this can be optimized as follows:
#              #    if reiterable_iter.__length_hint__():
#              #        return next(reiterable_iter)
#              #    else:
#              #        ...
#              #
#              #The issue, of course, is that that *ONLY* works for strict type
#              #hints constrained to C-based iterables (e.g.,
#              #"typing.Dict[...]"). General-purpose type hints like
#              #"typing.Mapping[...]" would be inapplicable, sadly. For the
#              #latter, dynamically testing for the existence of a semantically
#              #meaningful __length_hint__() getter would consume far more time
#              #than calling that getter would actually save. *shrug*
#              try:
#                  return next(reiterable_iter)
#              except StopIteration:
#                  #FIXME: Violates DRY a bit, but more efficient. *shrug*
#                  reiterable_weakproxy = _REITERABLE_ID_TO_WEAKPROXY[
#                      REITERABLE_ID]
#                  _REITERABLE_ID_TO_ITER[REITERABLE_ID] = iter(
#                      reiterable_weakproxy)
#                  return next(reiterable_iter)
#
#          if len(_REITERABLE_ID_TO_WEAKPROXY) >= _REITERABLE_CACHE_MAX_LEN:
#               #FIXME: Efficiently kick out the least-used item from both the
#               #"_REITERABLE_ID_TO_WEAKPROXY" and "_REITERABLE_ID_TO_ITER"
#               #dictionaries here. Research exactly how to do that. Didn't we
#               #already implement an efficient LRU somewhere in @beartype?
#
#          reiterable_weakproxy = _REITERABLE_ID_TO_WEAKPROXY[REITERABLE_ID] = (
#              proxy(reiterable))
#          _REITERABLE_ID_TO_ITER[REITERABLE_ID] = iter(reiterable_weakproxy)
#          return next(reiterable_iter)
#FIXME: Pretty boss, if we do say so. And we do. There are also considerable
#opportunities for both macro- and microoptimization. The biggest
#macrooptimization would be doing away entirely with the
#"_REITERABLE_ID_TO_WEAKPROXY" cache. Strictly speaking, we only actually need
#the "_REITERABLE_ID_TO_ITER" cache. Doing away with the
#"_REITERABLE_ID_TO_WEAKPROXY" cache is *PROBABLY* the right thing to do in most
#cases. Why? Because we don't necessarily expect that @beartype type-checkers
#will exhaust all available items for most reiterables. But we *DO* know that
#all reiterables that will be type-checked will be type-checked at least once.
#In other words, the trailing code in _get_reiterable_item_next() is guaranteed
#to *ALWAYS* happen at least once per reiterable (so we should optimize that);
#conversely, the leading code that restarts iteration from the beginning only
#happens in edge cases for smaller reiterables passed or returned frequently
#between @beartype-decorated callables (so we shouldn't bother optimizing that).
#Optimizing away "_REITERABLE_ID_TO_WEAKPROXY" then yields:
#
#      #FIXME: Don't even bother calling this getter with "dict" objects. The
#      #caller should explicitly perform an "pith.__class__ is dict" check to
#      #switch to more efficient "next(iter(pith.keys())" and
#      #"next(iter(pith.values())" logic when the pith is a "dict" object. Note
#      #that user-defined "dict" subclasses are fine, however. *facepalm*
#      def _get_reiterable_item_next(
#          reiterable: _BeartypeReiterableTypes) -> object:
#
#          REITERABLE_TYPE = reiterable.__class__
#
#          #FIXME: Again, optimize ...get() method access, please.
#          reiterable_is_weakreffable = (
#              _REITERABLE_TYPE_TO_IS_WEAKREFFABLE.get(REITERABLE_TYPE))
#
#          if reiterable_is_weakreffable is None:
#              reiterable_dict = getattr(reiterable, '__dict__')
#              #FIXME: Alternately, we could try just taking a weak proxy
#              #of this reiterable and catching exceptions. Although
#              #slower, this caching operation only occurs once per type.
#              #For now, let's run with this faster heuristic.
#              if not reiterable_dict:
#                  reiterable_is_weakreffable = False
#              else:
#                  reiterable_slots = reiterable_dict.get('__slots__')
#                  reiterable_is_weakreffable = (
#                      reiterable_slots and
#                      '__weakref__' not in reiterable_slots
#                  )
#              _REITERABLE_TYPE_TO_IS_WEAKREFFABLE[REITERABLE_TYPE] = (
#                  reiterable_is_weakreffable)
#
#          # If this reiterable is a C-based container that does *NOT* support
#          # weak references, reduce to simply returning the first item of this
#          # reiterable.
#          if not reiterable_is_weakreffable:
#              return next(iter(reiterable))
#
#          REITERABLE_ID = id(reiterable)
#
#          #FIXME: Optimize by storing and calling a bound
#          #"_REITERABLE_ID_TO_ITER_get" method instead, please.
#          reiterable_iter = _REITERABLE_ID_TO_ITER.get(REITERABLE_ID)
#
#          if reiterable_iter:
#              #FIXME: Optimize us up, yo!
#              if _REITERABLE_TYPE_TO_IS_LENGTHHINTED.get(REITERABLE_TYPE):
#                  if reiterable_iter.__length_hint__():
#                      return next(reiterable_iter)
#              else:
#                  try:
#                      return next(reiterable_iter)
#                  except StopIteration:
#                      pass
#          elif len(_REITERABLE_ID_TO_ITER) >= _REITERABLE_CACHE_MAX_LEN:
#               #FIXME: Efficiently kick out the least-used item from the
#               #"_REITERABLE_ID_TO_ITER" dictionary here. Research exactly how
#               #to do that. Didn't we already implement an efficient LRU
#               #somewhere in @beartype?
#               #FIXME: *AH-HA!* Forget LRU. Seriously. LRU would impose too
#               #much overhead here, as we'd need to update the LRU on each
#               #access. Instead, let's just friggin *CLEAR* the entire cache
#               #here. Yes, that's right! Nuke it from orbit, bois! So, what?
#               #Right? Who cares if we start over from zero? Nobody! It's
#               #minimal overhead to just start iterating things all over again.
#               #And if the cache is full up, that's a good indication that the
#               #caller has gone off the rails a bit, anyway.
#               _REITERABLE_ID_TO_ITER.clear()  # <-- *BOOM STICK*
#
#          reiterable_iter = _REITERABLE_ID_TO_ITER[REITERABLE_ID] = iter(
#              proxy(reiterable))
#          return next(reiterable_iter)
#
#Seems legitimately boss, yes? Everything above is feasible and *REASONABLY*
#efficient -- but is that efficient enough? Honestly, that's probably fast
#enough for *MOST* use cases. If users justifiably complain about performance
#degradations, we could always provide a new "BeartypeConf" parameter defaulting
#to enabled to control this behaviour. *shrug*

#FIXME: Note that randomly checking mapping (e.g., "dict") keys and/or values
#will be non-trivial, as there exists no out-of-the-box O(1) approach in either
#the general case or the specific case of a "dict". Actually, there does -- but
#we'll need to either internally or externally maintain one dict.items()
#iterator for each passed mapping. We should probably investigate the space
#costs of that *BEFORE* doing so. Assuming minimal costs, one solution under
#Python >= 3.8 might resemble:
#* Define a new _get_dict_random_key() function resembling:
#      def _get_dict_nonempty_random_key(mapping: MappingType) -> object:
#          '''
#          Caveats
#          ----------
#          **This mapping is assumed to be non-empty.** If this is *not* the
#          case, this function raises a :class:`StopIteration` exception.
#          '''
#          items_iter = getattr(mapping, '__beartype_items_iter', None)
#          if items_iter is None:
#              #FIXME: This should probably be a weak reference to prevent
#              #unwanted reference cycles and hence memory leaks.
#              #FIXME: We need to protect this both here and below with a
#              #"try: ... except Exception: ..." block, where the body of the
#              #"except Exception:" condition should probably just return
#              #"beartype._util.utilobject.SENTINEL", as the only type hints
#              #that would ever satisfy are type hints *ALL* objects satisfy
#              #(e.g., "Any", "object").
#              mapping.__beartype_items_iter = iter(mapping.items())
#          try:
#              return next(mapping.__beartype_items_iter)
#          # If we get to the end (i.e., the prior call to next() raises a
#          # "StopIteration" exception) *OR* anything else happens (i.e., the
#          # prior call to next() raises a "RuntimeError" exception due to the
#          # underlying mapping having since been externally mutated), just
#          # start over. :p
#          except Exception:
#              mapping.__beartype_items_iter = None
#
#              # We could also recursively call ourselves: e.g.,
#              #     return _get_dict_random_key(mapping)
#              # However, that would be both inefficient and dangerous.
#              mapping.__beartype_items_iter = iter(mapping.items())
#              return next(mapping.__beartype_items_iter)
#* In "beartype._decor._main":
#     import _get_dict_nonempty_random_key as __beartype_get_dict_nonempty_random_key
#* In code generated by this submodule, internally call that helper when
#  checking keys of non-empty mappings *THAT ARE UNSLOTTED* (for obvious
#  reasons) ala:
#  (
#     {hint_curr_pith} and
#     not hasattr({hint_curr_pith}, '__slots__') and
#     {!INSERT_CHILD_TEST_HERE@?(
#         {hint_child_pith} := __beartype_get_dict_nonempty_random_key({hint_curr_pith}))
#  )
#  Obviously not quite right, but gives one the general gist of the thing.
#
#We could get around the slots limitation by using an external LRU cache
#mapping from "dict" object ID to items iterator, and maybe that *IS* what we
#should do. Actually... *NO.* We absolutely should *NOT* do that sort of thing
#anywhere in the codebase, as doing so would guaranteeably induce memory leaks
#by preventing "dict" objects cached in that LRU from being garbage collected.
#
#Note that we basically can't do this under Python < 3.8, due to the lack of
#assignment expressions there. Since _get_dict_nonempty_random_key() returns a
#new random key each call, we can't repeatedly call that for each child pith
#and expect the same random key to be returned. So, Python >= 3.8 only. *shrug*
#
#Note that the above applies to both immutable mappings (i.e., objects
#satisfying "Mapping" but *NOT* "MutableMapping"), which is basically none of
#them, and mutable mappings. Why? Because we don't particularly care if the
#caller externally modifies the underlying mapping between type-checks, even
#though the result is the above call to "next(mapping.__beartype_items_iter)"
#raising a "RuntimeError". Who cares? Whenever an exception occurs, we just
#restart iteration over from the beginning and carry on. *GOOD 'NUFF.*
#FIXME: *YIKES.* So, as expected, the above approach fundamentally fails on
#builtin dicts and sets. Why? Because *ALL* builtin types prohibit
#monkey-patching, which the above technically is. Instead, we need a
#fundamentally different approach.
#
#That approach is to globally (but thread-safely, obviously) cache *STRONG*
#references to iterators over dictionary "ItemsView" objects. Note that we
#can't cache weak references, as the garbage collector would almost certainly
#immediately dispose of them, entirely defeating the point. Of course, these
#references implicitly prevent garbage collection of the underlying
#dictionaries, which means we *ALSO* need a means of routinely removing these
#references from our global cache when these references are the only remaining
#references to the underlying dictionaries. Can we do any of this? We can.
#
#First, note that we can trivially obtain the number of live references to any
#arbitrary object by calling "sys.getrefcount(obj)". Note, however, that the
#count returned by this function is mildly non-deterministic. In particular,
#off-by-one issues are not merely edge cases but commonplace. Ergo:
#
#    from sys import getrefcount
#
#    def is_obj_nearly_dead(obj: object) -> bool:
#        '''
#        ``True`` only if there only exists one external strong reference to
#        the passed object.
#        '''
#
#        # Note that the integer returned by this getter is intentionally *NOT*
#        # tested for equality with "1". Why? Because:
#        # * The "obj" parameter passed to this tester is an ignorable strong
#        #   reference to this object.
#        # * The "obj" parameter passed to the getrefcount() getter is yet
#        #   another strong reference to this object.
#        return getrefcount(obj) <= 3
#
#Second, note that neither the iterator API nor the "ItemsView" API provide a
#public means of obtaining a strong reference to the underlying dictionary.
#This means we *MUST* necessarily maintain for each dictionary a 2-tuple
#"(mapping, mapping_iter)", where:
#* "mapping" is a strong reference to that dictionary.
#* "mapping_iter" is an iterator over that dictionary's "ItemsView" object.
#
#This implies that we want to:
#* Define a new "beartype._util.cache.utilcachemapiter" submodule.
#* In that submodule:
#  * Define a new global variable resembling:
#      # Note that this is unbounded. There's probably no reasonable reason to
#      # use an LRU-style bounded cache here... or maybe there is for safety to
#      # avoid exhausting memory. Right.
#      #
#      # So, this should obviously be LRU-bounded at some point. Since Python's
#      # standard @lru decorator is inefficient, we'll need to build that our
#      # ourselves, which means this is *NOT* an immediate priority.
#      _MAP_ITER_CACHE = {}
#      '''
#      Mapping from mapping identifiers to 2-tuples
#      ``(mapping: Mapping, mapping_iter: Iterator)``,
#      where ``mapping`` is a strong reference to the mapping whose key is that
#      mapping's identifier and ``mapping_iter`` is an iterator over that
#      mapping's ``ItemsView`` object.
#      '''
#  * Define a new asynchronous cleanup_cache() function. See the
#    cleanup_beartype() function defined below for inspiration.
#* Extensively unit test that submodule.
#
#Third, note that this means the above is_obj_nearly_dead() fails to apply to
#this edge case. In our case, a cached dictionary is nearly dead if and only if
#the following condition applies:
#
#    def is_cached_mapping_nearly_dead(mapping: Mapping) -> bool:
#        '''
#        ``True`` only if there only exists one external strong reference to
#        the passed mapping internally cached by the :mod:`beartype.beartype`
#        decorator.
#        '''
#
#        # Note that the integer returned by this getter is intentionally *NOT*
#        # tested for equality with "1". Why? Because ignorable strong
#        # references to this mapping include:
#        # * The "mapping" parameter passed to this tester.
#        # * The "mapping" parameter passed to the getrefcount() getter.
#        # * This mapping cached by the beartype-specific global container
#        #   caching these mappings.
#        # * The iterator over this mapping cached by the same container.
#        return getrefcount(mapping) <= 5   # <--- yikes!
#
#Fourth, note that there are many different means of routinely removing these
#stale references from our global cache (i.e., references that are the only
#remaining references to the underlying dictionaries). For example, we could
#routinely iterate over our entire cache, find all stale references, and remove
#them. This is the brute-force approach. Of course, this approach is both slow
#and invites needlessly repeated work across repeated routine iterations. Ergo,
#rather than routinely iterating *ALL* cache entries, we instead only want to
#routinely inspect a single *RANDOM* cache entry on each scheduled callback of
#our cleanup routine. This is the O(1) beartype approach and still eventually
#gets us where we want to go (i.e., complete cleanup of all stale references)
#with minimal costs. A random walk wins yet again.
#
#Fifth, note that there are many different means of routinely scheduling work.
#We ignore the existence of the GIL throughout the following discussion, both
#because we have no choice *AND* because the randomized cleanup we need to
#perform on each scheduled callback is an O(1) operation with negligible
#constant factors and thus effectively instantaneous rather than CPU- or
#IO-bound. The antiquated approach is "threading.Timer". The issue with the
#entire "threading" module is that it is implemented with OS-level threads,
#which are ludicrously expensive and thus fail to scale. Our usage of the
#"threading" module in beartype would impose undue costs on downstream apps by
#needlessly consuming a precious thread, preventing apps from doing so. That's
#bad. Instead, we *MUST* use coroutines, which are implemented in Python itself
#rather than exposed to the OS and thus suffer no such scalability concerns,
#declared as either:
#* Old-school coroutines via the @asyncio.coroutine decorator. Yielding under
#  this approach is trivial (and possibly more efficient): e.g.,
#       yield
#* New-school coroutines via the builtin "async def" syntax. Yielding under
#  this approach is non-trivial (and possibly less efficient): e.g.,
#       await asyncio.sleep_ms(0)
#
#In general, the "async def" approach is strongly favoured by the community.
#Note that yielding control in the "async def" approach is somewhat more
#cumbersome and possibly less efficient than simply performing a "yield".
#Clearly, a bit of research here is warranted. Note this online commentary:
#    In performance-critical code yield does offer a small advantage. There are
#    other tricks such as yielding an integer (number of milliseconds to
#    pause). In the great majority of cases code clarity trumps the small
#    performance gain achieved by these hacks. In my opinion, of course.
#
#In either case, we declare an asynchronous coroutine. We then need to schedule
#that coroutine with the global event loop (if any). The canonical way of doing
#this is to:
#* Pass our "async def" function to the asyncio.create_task() function.
#  Although alternatives exist (e.g., futures), this function is officially
#  documented as being the preferred approach:
#    create_task() (added in Python 3.7) is the preferable way for spawning new
#    tasks.
#  Of course, note this requires Python >= 3.7. We could care less. *shrug*
#* Pass that task to the asyncio.run() function... or something, something.
#  Clearly, we still need to research how to routinely schedule that task with
#  "asyncio" rather than running it only once. In theory, that'll be trivial.
#
#Here's a simple example:
#
#    async def cleanup_beartype(event_loop):
#        # Disregard how simple this is, it's just for example
#        s = await asyncio.create_subprocess_exec("ls", loop=event_loop)
#
#    def schedule_beartype_cleanup():
#        event_loop = asyncio.get_event_loop()
#        event_loop.run_until_complete(asyncio.wait_for(
#            cleanup_beartype(event_loop), 1000))
#
#The above example was culled from this StackOverflow post:
#    https://stackoverflow.com/questions/45010178/how-to-use-asyncio-event-loop-in-library-function
#Unlike the asyncio.create_task() approach, that works on Python >= 3.6.
#Anyway, extensive research is warranted here.
#
#Sixthly, note that the schedule_beartype_cleanup() function should be called
#only *ONCE* per active Python process by the first call to the @beartype
#decorator passed a callable annotated by one or more "dict" or
#"typing.Mapping" type hints. We don't pay these costs unless we have to. In
#particular, do *NOT* unconditionally call the schedule_beartype_cleanup()
#function on the first importation of the "beartype" package.
#
#Lastly, note there technically exists a trivial alternative to the above
#asynchronous approach: the "gc.callbacks" list, which allows us to schedule
#arbitrary user-defined standard non-asynchronous callback functions routinely
#called by the garbage collector either immediately before or after each
#collection. So what's the issue? Simple: end users are free to either
#explicitly disable the garbage collector *OR* compile or interpreter their
#apps under a non-CPython executable that does not perform garbage collection.
#Ergo, this alternative fails to generalize and is thus largely useless.
#FIXME: Actually... let's not do the "asyncio" approach -- at least not
#initially. Why? The simplest reason is that absolutely no one expects a
#low-level decorator to start adding scheduled asynchronous tasks to the global
#event loop. The less simple reason is that doing so would probably have
#negative side effects to at least one downstream consumer, the likes of which
#we could never possibly predict.
#
#So, what can we do instead? Simple. We do this by:
#* If garbage collection is enabled, registering a new cleanup callback with
#  "gc.callbacks".
#* Else, we get creative. First, note that garbage collection is really only
#  ever disabled in the real world when compiling Python to a lower-level
#  language (typically, C). Ergo, efficiency isn't nearly as much of a concern
#  in this currently uncommon edge case. So, here's what we do:
#  * After the first call to the @beartype decorator passed a callable
#    annotated by one or more mapping or set type hints, globally set a private
#    "beartype" boolean -- say, "WAS_HINT_CLEANABLE" -- noting this to have
#    been the case.
#  * In the _code_check_params() function generating code type-checking *ALL*
#    annotated non-ignorable parameters:
#    * If "WAS_HINT_CLEANABLE" is True, conditionally append code calling our
#      cleanup routine *AFTER* code type-checking these parameters. While
#      mildly inefficient, function calls incur considerably less overhead
#      when compiled away from interpreted Python bytecode.
#FIXME: Note that the above scheme by definition *REQUIRES* assignment
#expressions and thus Python >= 3.8 for general-purpose O(1) type-checking of
#arbitrarily nested dictionaries and sets. Why? Because each time we iterate an
#iterator over those data structures we lose access to the previously iterated
#value, which means there is *NO* sane means of type-checking nested
#dictionaries or sets without assignment expressions. But that's unavoidable
#and Python <= 3.7 is the past, so that's largely fine.
#
#What we can do under Python <= 3.7, however, is the following:
#* If the (possibly nested) type hint is of the form
#  "{checkable}[...,{dict_or_set}[{class},{class}],...]" where
#  "{checkable}" is an arbitrary parent type hint safely checkable under Python
#  <= 3.7 (e.g., lists, unions), "{dict_or_set}" is (wait for it) either "dict"
#  or "set", and "{class}" is an arbitrary type, then that hint *IS* safely
#  checkable under Python <= 3.7. Note that items (i.e., keys and values) can
#  both be checked in O(1) time under Python <= 3.7 by just validating the key
#  and value of a different key-value pair (e.g., by iterating once for the key
#  and then again for the value). That does have the disadvantage of then
#  requiring O(n) iteration to raise a human-readable exception if a dictionary
#  value fails a type-check, but we're largely okay with that. Again, this only
#  applies to an edge case under obsolete Python versions, so... *shrug*
#* Else, a non-fatal warning should be emitted and the portion of that type
#  hint that *CANNOT* be safely checked under Python <= 3.7 should be ignored.
#FIXME: Note that mapping views now provide a "mapping" attribute enabling
#direct access of the mapping mapped by that view under Python >= 3.10:
#    The views returned by dict.keys(), dict.values() and dict.items() now all
#    have a mapping attribute that gives a types.MappingProxyType object
#    wrapping the original dictionary.
#This means that we do *NOT* need to explicitly cache the "mapping" object
#mapped by any cached view under Python >= 3.10, reducing space consumption.

#FIXME: *WOOPS.* The "CacheLruStrong" class is absolutely awesome and we'll
#absolutely be reusing that for various supplementary purposes across the
#codebase (e.g., for perfect O(1) tuple type-checking below). However, this
#class sadly doesn't get us where we need to be for full O(1) dictionary and
#set type-checking. Why? Two main reasons:
#* *ITERATIVE ACCESS.* Our routinely scheduled cleanup function needs to
#  iteratively or randomly access arbitrary cache items for inspection to
#  decide whether they need to be harvested or not.
#* *VARIABLE OBJECT SIZES.* We gradually realized, given the plethora of
#  related "FIXME:" comments below, that we'll eventually want to cache a
#  variety of possible types of objects across different caches -- each cache
#  caching a unique type of object. This makes less and less sense the more one
#  considers, however. For example, why have an LRU cache of default size 256
#  specific to iterators for a downstream consumer that only passes one
#  iterator to a single @beartype-decorated callable?
#
#The solution to both is simple, but not: we define a new derivative
#"LRUDuffleCacheStrong" class. The motivation for using the term "duffle" is
#that, just like a duffle bag, a duffle cache:
#* Provides random access.
#* Elegantly stretches to contains a variable number of arbitrary objects of
#  variable size.
#
#The "LRUDuffleCacheStrong" class satisfies both concerns by caching to a
#maximum *OBJECT SIZE CAPACITY* rather than merely to an *OBJECT NUMBER
#CAPACITY.* Whereas the "CacheLruStrong" class treats all cached objects as
#having a uniform size of 1, the "LRUDuffleCacheStrong" class instead assigns
#each cached object an estimated abstract size (EAS) as a strictly positive
#integer intended to reflect its actual transitive in-memory size -- where a
#cached object of EAS 1 is likely to be the smallest object in that cache.
#While estimating EAS will depend on object type, the following should apply:
#* EAS estimators *MUST* run in O(1) time. That is, estimating the abstract
#  size of an object *MUST* be implementable in constant time with negligible
#  constant factors. This means that the standard approach of recursively
#  inspecting the physical in-memory sizes of all objects visitable from the
#  target object should *NOT* be employed.
#* For containers:
#  * Note that type hints provide us the expected height
#    "sizeable_height" of any data structure, where "sizeable_height" is
#    defined as the number of "[" braces in a type hint ignoring those that do
#    *NOT* connote semantic depth (e.g., "Optional", "Union", "Annotated"). So:
#    * The "sizeable_height" for a type hint "list[list[list[int]]]" is 3.
#    * Since any unsubscripted type hint (e.g., "list") is implicitly
#      subscripted by "[Any]", the "sizeable_height" for the type hints "list"
#      and "list[int]" is both 1.
#  * Note also that most containers satisfy the "collections.abc.Sizeable" ABC.
#  * Given that, we can trivially estimate the EAS "sizeable_bigo_size" of any
#    type-hinted sizeable object "sizeable" as follows:
#      sizeable_bigo_size = len(sizeable) ** sizeable_height
#  Ergo, a list of length 100 type-hinted as "list[list[int]]" has a size of:
#      sizeable_bigo_size = 100 ** 2 = 10,000
#* For dictionaries, the "sizeable_bigo_size" provided by the equation above
#  should be multiplied by two to account for the increased space consumption
#  due to storing key-value pairs.
#
#Here's then how the "LRUDuffleCacheStrong" class is implemented:
#* The "LRUDuffleCacheStrong" class should *NOT* subclass the
#  "CacheLruStrong" class but copy-and-paste from the latter into the former.
#  This is both for efficiency and maintainability; it's likely their
#  implementations will mildly diverge.
#* The LRUDuffleCacheStrong.__init__() method should be implemented like this:
#      def __init__(
#          self,
#          bigo_size_max: int,
#          value_metadata_len: 'Optional[int]' = 0,
#      )
#          assert bigo_size_max > 0
#          assert value_metadata_len >= 0
#
#          # Classify all passed parameters as instance variables.
#          self._EAS_MAX = bigo_size_max
#          self._FIXED_LIST_SIZE = value_metadata_len + 2
#
#          # Initialize all remaining instance variables.
#          self._bigo_size_cur = 0
#          self._iter = None
#* Note the above assignment of these new instance variables:
#  * "_EAS_MAX", the maximum capacity of this LRU cache in EAS units. Note that
#    this capacity should ideally default to something that *DYNAMICALLY SCALES
#    WITH THE RAM OF THE LOCAL MACHINE.* Ergo, "_bigo_size_max" should be
#    significantly larger in a standard desktop system with 32GB RAM than it is
#    on a Raspberry Pi 2 with 1GB RAM: specifically, 32 times larger.
#  * "_bigo_size_cur", the current capacity of this LRU cache in EAS units.
#  * "_FIXED_LIST_SIZE", the number of additional supplementary objects to
#    be cached with each associated value of this LRU cache. The idea here is
#    that each key-value pair of this cache is an arbitrary hashable object
#    (the key) mapping to a "FixedList(size=self._FIXED_LIST_SIZE)"
#    (the value) whose 0-based indices provide (in order):
#    1. The EAS of that object. For completeness, we should also add to the
#       "sizeable_bigo_size" estimate given above the additional estimated cost
#       of this "FixedList". Since the length of this "FixedList" is guaranteed
#       to be exactly "self._value_metadata_len + 2", this then gives a final
#       EAS of that object as:
#         sizeable_bigo_size = (
#             self._value_metadata_len + 2 + len(sizeable) ** sizeable_height)
#    2. A strong reference to the primary object being cached under this key.
#       For dictionaries and sets, this is an iterator over those dictionaries
#       and sets.
#    3...self._value_metadata_len + 2: Additional supplementary objects to be
#       cached along with that object. For dictionaries and sets, exactly one
#       supplementary object must be cached, so this is:
#       3. The underlying dictionary or set being iterated over, so we can
#          lookup the number of existing strong references to that dictionary
#          or set during cleanup and decide whether to uncache that or not.
#  * "_iter", an iterator over this dictionary. Yes, we *COULD* implement
#    random access (e.g., with a linked list or list), but doing so introduces
#    extreme complications and inefficiencies in both space and time. Instead,
#    persisting a simple iterator over this dictionary suffices.
#* Allow any "LRUDuffleCacheStrong" instance to be trivially incremented
#  (e.g., during garbage collection cleanup) as an iterator by also defining:
#      def get_pair_next_or_none(
#          self,
#          __dict_len = dict.__len__,
#      ) -> 'Optional[Tuple[Hashable, FixedList]]':
#          '''
#          Next most recently used key-value pair of this cache if this cache
#          is non-empty *or* ``None`` otherwise (i.e., if this cache is empty).
#
#          The first call to this method returns the least recently used
#          key-value pair of this cache. Each successive call returns the next
#          least recently used key-value pair of this cache until finally
#          returning the most recently used key-value pair of this cache, at
#          which time the call following that call rewinds time by again
#          returning the least recently used key-value pair of this cache.
#          '''
#
#          #FIXME: Probably nest this in a "with self._thread_lock:" block.
#
#          # If this cache is empty, return None.
#          if not __dict_len(self):
#              return None
#          # Else, this cache is non-empty.
#
#          # Attempt to...
#          try:
#              # Return the next recent key-value pair of this cache.
#              return self._iter.__next__()
#          # If doing so raises *ANY* exception, this iterator has become
#          # desynchronized from this cache. In this case...
#          #
#          # Note this implicitly handles the initial edge case in which this
#          # cache has yet to be iterated (i.e., "self._iter == None"). Since
#          # this is *ONLY* the case for the first call to this method for the
#          # entire lifetime of the active Python process, the negligible
#          # overhead of handling this exception is preferable to violating DRY
#          # by duplicating this logic with an explicit
#          # "if self._iter == None:" block.
#          except:
#              # Reinitialize this iterator.
#              self._iter = self.items()
#
#              # Return the least recent such pair.
#              return self._iter.__next__()
#* Refactor the __setitem__() method. Specifically, when caching a new
#  key-value pair with EAS "bigo_size_item" such that:
#      while bigo_size_item + self._bigo_size_cur > self._bigo_size_max:
#  ...we need to iteratively remove the least recently used key-value pair of
#  this cache (which, yes, technically has O(n) worst-case time, which is
#  non-ideal, which may be why nobody does this, but that's sort-of okay here,
#  since we're doing something monstrously productive each iteration by freeing
#  up critical space and avoiding memory leaks, which seems more than worth the
#  cost of iteration, especially as we expect O(1) average-case time) until
#  this cache can fit that pair into itself. Once it does, we:
#      # Bump the current EAS of this cache by the EAS of this pair.
#      self._bigo_size_cur += bigo_size_item
#  Oh, and there's an obvious edge case here: if "bigo_size_item >
#  self._bigo_size_max", we do *NOT* attempt to do anything with that object.
#  We don't cache it or an iterator over it. It's too bid. Instead, we just
#  type-check the first item of that object in O(1) time. *shrug*
#
#Seems sweet to us. We can store arbitrarily large nested containers in our
#duffle cache without exhausting memory, which is actually more than the
#brute-force LRU cache can say. We get trivial iteration persistence. We also
#avoid a proliferation of different LRU caches, because a single
#"LRUDuffleCacheStrong" instance can flexibly store heterogeneous types.
#FIXME: *RIGHT.* So, "LRUDuffleCacheStrong" is mostly awesome as defined above.
#We'd just like to make a few minor tweaks for improved robustness:
#
#* Drop the "value_metadata_len" parameter from the
#  LRUDuffleCacheStrong.__init__() method. We'd prefer to have that parameter
#  individually passed to each cache_item() call (see below) rather than
#  globally, as the former enables different types of cached objects to have a
#  different quantity of metadata cached with those objects.
#* Drop the __setitem__() implementation borrow from "CacheLruStrong". Instead,
#  defer to the existing dict.__setitem__() implementation. Why? Because we
#  need to pass additional cache-specific parameters to our own
#  __setitem__()-like non-dunder method, which __setitem__() doesn't support.
#* Define a new cache_obj() method resembling CacheLruStrong.__setitem__() but
#  even more virile and awesome with signature resembling:
#      def cache_value(
#          self,
#
#          # Mandatory parameters.
#          key: 'Hashable',
#          value: object,
#          *metadata: object,
#
#          # Optional parameters.
#          value_height: 'Optional[int]' = 1,
#      ) -> None:

#FIXME: Here's a reasonably clever idea for perfect O(1) tuple type-checking
#guaranteed to check all n items of an arbitrary tuple in exactly n calls, with
#each subsequent call performing *NO* type-checking by reducing to a noop. How?
#Simple! We:
#* Augment our existing "CacheLruStrong" data structure to optionally accept a
#  new initialization-time "value_maker" factory function defaulting to "None".
#  If non-"None", "CacheLruStrong" will implicitly call that function on each
#  attempt to access a missing key by assigning the object returned by that
#  call as the key of a new key-value pair -- or, in other words, by behaving
#  exactly like "collections.defaultdict".
#* Globally define a new "_LRU_CACHE_TUPLE_TO_COUNTER" cache somewhere as an
#  instance of "CacheLruStrong" whose "value_maker" factory function is
#  initialized to a lambda function simply returning a new
#  "collections.Counter" object that starts counting at 0. Since tuples
#  themselves are hashable and thus permissible for direct use as dictionary
#  keys, this cache maps from tuples (recently passed to or returned from
#  @beartype-decorated callables) to either:
#  * If that tuple has been type-checked to completion, "True" or any other
#    arbitrary sentinel placeholder, really. "True" is simpler, however,
#    because the resulting object needs to be accessible from dynamically
#    generated wrapper functions.
#  * Else, a counter such that the non-negative integer returned by
#    "next(counter)" is the 0-based index of the next item of that tuple to be
#    type-checked.
#
#Given that low-level infrastructure, the make_func_wrapper_code() function below
#then generates code perfectly type-checking arbitrary tuples in O(1) time that
#should ideally resemble (where "__beartype_pith_j" is the current pith
#referring to this tuple):
#    (
#        _LRU_CACHE_TUPLE_TO_COUNTER[__beartype_pith_j] is True or
#        {INSERT_CHILD_TYPE_CHECK_HERE}(
#            __beartype_pith_k := __beartype_pith_j[
#                next(_LRU_CACHE_TUPLE_TO_COUNTER[__beartype_pith_j])]
#        )
#    )
#
#Awesome, eh? The same concept trivially generalizes to immutable sequences
#(i.e., "Sequence" type hints that are *NOT* "MutableSequence" type hints).
#Sadly, since many users use "Sequence" to interchangeably denote both
#immutable and mutable sequences, we probably have no means of reliably
#distinguishing the two. So it goes! So, just tuples then in practice. *sigh*

#FIXME: Huzzah! We finally invented a reasonably clever means of (more or less)
#safely type-checking one-shot iterables like generators and iterators in O(1)
#time without destroying those iterables. Yes, doing so requires proxying those
#iterables with iterables of our own. Yes, this is non-ideal but not nearly as
#bad as you might think. Why? Because *NO ONE CARES ABOUT ONE-SHOT ITERABLES.*
#They're one-shot. By definition, you can't really care about them, because
#they don't last long enough. You certainly can't cache them or stash them in
#data structures or really do anything with them beside pass or return them
#between callables until they inevitably get exhausted.
#
#This means that proxying one-shot iterables is almost always safe. Moreover,
#we devised a clever means of proxying that introduces negligible overhead
#while preserving our O(1) guarantee. First, let's examine the standard
#brute-force approach to proxying one-shot iterables:
#
#    class BeartypeIteratorProxy(object):
#        def __init__(self, iterator: 'Iterator') -> None:
#            self._iterator = iterator
#
#        def __next__(self) -> object:
#            item_next = next(self._iterator)
#
#            if not {INSERT_TYPE_CHECKS_HERE}(item_next):
#                raise SomeBeartypeException(f'Iterator {item_next} bad!')
#
#            return item_next
#
#That's bad, because that's an O(n) type-check run on every single iteration.
#Instead, we do this:
#
#    class BeartypeIteratorProxy(object):
#        def __init__(self, iterator: 'Iterator') -> None:
#            self._iterator = iterator
#
#        def __next__(self) -> object:
#            # Here is where the magic happens, folks.
#            self.__next__ = self._iterator.__next__
#
#            item_next = self.__next__(self._iterator)
#
#            if not {INSERT_TYPE_CHECKS_HERE}(item_next):
#                raise SomeBeartypeException(f'Iterator {item_next} bad!')
#
#            return item_next
#
#See what we did there? We dynamically monkey-patch away the
#BeartypeIteratorProxy.__next__() method by replacing that method with the
#underlying __next__() method of the proxied iterator immediately after
#type-checking one and only one item of that iterator.
#
#The devil, of course, is in that details. Assuming a method can monkey-patch
#itself away (we're pretty sure it can, as that's the basis of most efficient
#decorators that cache property method results, *BUT WE SHOULD ABSOLUTELY
#VERIFY THAT THIS IS THE CASE), the trick is then to gracefully handle
#reentrancy. That is to say, although we have technically monkey-patched away
#the BeartypeIteratorProxy.__next__() method, that object is still a live
#object that *WILL BE RECREATED ON EACH CALL TO THE SAME* @beartype-decorated
#callable. Yikes! So, clearly we yet again cache with an "CacheLruStrong" cache
#specific to iterators... or perhaps something like "CacheLruStrong" that
#provides a callback mechanism to enable arbitrary objects to remove themselves
#from the cache. Yes! Perhaps just augment our existing "CacheLruStrong" strong
#with some sort of callback or hook support?
#
#In any case, the idea here is that the "BeartypeIteratorProxy" class defined
#above should internally:
#* Store a weak rather than strong reference to the underlying iterator.
#* Register a callback with that weak reference such that:
#  * When the underlying iterator is garbage-collected, the wrapping
#    "BeartypeIteratorProxy" proxy removes itself from its "CacheLruStrong"
#    proxy.
#
#Of course, we're still not quite done yet. Why? Because we want to avoid
#unnecessarily wrapping "BeartypeIteratorProxy" instances in
#"BeartypeIteratorProxy" instances. This will happen whenever such an instance
#is passed to a @beartype-decorated callable annotated as accepting or
#returning an iterator. How can we avoid that? Simple. Whenever we detect that
#an iterator to be type-checked is already a "BeartypeIteratorProxy" instance,
#we just efficiently restore the __next__() method of that instance to its
#pre-monkey-patched version: e.g.,
#    (
#        isinstance(__beartype_pith_n, BeartypeIteratorProxy) and
#        # Unsure if this sort of assignment expression hack actually works.
#        # It probably doesn't. So, this may need to be sealed away into a
#        # utility function performing the same operation. *shrug*
#        __beartype_pith_n.__next__ = BeartypeIteratorProxy.__next__
#    )

#FIXME: Huzzah! The prior commentary on type-checking iterators in O(1) time
#also generalizes to most of the other non-trivial objects we had no idea how
#to type-check -- notably, callables. How? Simple. *WE PROXY CALLABLES WITH
#OBJECTS WHOSE* __call__() methods:
#* Type-check parameters to be passed to the underlying callable.
#* Call the underlying callable.
#* Type-check the return value.
#* Monkey-patch themselves away by replacing themselves (i.e., the __call__()
#  methods of that object) with the underlying callable. The only issue here,
#  and it might be a deal-breaker, is whether or not a bound method can simply
#  be replaced with either an unbound function *OR* a bound method of another
#  object entirely. Maybe it can? We suspect it can in both cases, but research
#  will certainly be required here.
#
#Again, cache such objects to avoid reentrancy issues. That said, there is a
#significant complication here that one-shot iterables do *NOT* suffer:
#proxying. Unlike one-shot iterables, callables are often expected to retain
#their object identities. Proxying disrupts that. I still believe that we
#should enable proxying across the board by default despite that, because less
#than 1% of our users will manually enable an option enabling proxying, simply
#because they'll never think to go look for it and when they do find it will be
#understandably hesitant to enable it when everything else is working. Users
#(including myself) typically only enable options when they encounter issues
#requiring they do so. Ergo, proxy by default. But we *ABSOLUTELY* need to
#allow users to conditionally disable proxying on a per-decoration basis --
#especially when proxying callables.
#
#So we propose adding a new optional "is_proxying" parameter to the @beartype
#decorator. Unfortunately, doing so in an efficient manner will prove highly
#non-trivial. Why? Because the standard approach of doing so is *PROBABLY*
#extremely inefficient. We need to test that hypothesis, of course, but the
#standard approach to adding optional parameters to decorators is to nest a
#closure in a closure in a function. We don't need the innermost closure, of
#course, because we dynamically generate it at runtime. We would need the
#outermost closure, though, to support optional decorator parameters under the
#standard approach. That seems outrageously expensive, because each call to the
#@beartype decorator would then internally generate and return a new closure!
#Yikes. We can avoid that by instead, on each @beartype call:
#* Create a new functools.partial()-based wrapper decorator passed our
#  @beartype decorator and all options passed to the current @beartype call.
#* Cache that wrapper decorator into a new private "CacheLruStrong" instance.
#* Return that decorator.
#* Return the previously cached wrapper decorator on the next @beartype call
#  passed the same options (rather than recreating that decorator).
#
#Naturally, this requires these options to be hashable. Certainly, booleans
#are, so this smart approach supports a new optional "is_proxying" parameter.
#FIXME: Note that the above approach should only be employed as a last-ditch
#fallback in the event that the passed callable both:
#* Lacks a non-None "__annotations__" dictionary.
#* Is *not* annotated by the third-party optional "typeshed" dependency.
#
#If the passed callable satisfies either of those two constraints, the existing
#type hints annotating that callable should be trivially inspected instead in
#O(1) time (e.g., by just performing a brute-force dictionary comparison from
#that callable's "__annotations__" dictionary to a dictionary that we
#internally construct and cache based on the type hints annotating the
#currently decorated callable, except that doesn't quite work because the
#"__annotations__" dictionary maps from parameter and return names whereas the
#"typing.Callable" and "collections.abc.Callable" syntax omits those names,
#which begs the question of how the latter syntax handles positional versus
#keyword arguments anyway)... *OR SOMETHING.*
#
#Fascinatingly, "Callable" syntax supports *NO* distinction between mandatory,
#optional, positional, or keyword arguments, because PEP 484 gonna PEP 484:
#    "There is no syntax to indicate optional or keyword arguments; such
#     function types are rarely used as callback types."
#
#Note that mapping from the return type hint given by "typing.Callable" syntax
#into the "__annotations__" dictionary is trivial, because the return is always
#unconditionally named "return" in that dictionary. So, we then just have to
#resolve how to ignore parameter names. Actually, handling mandatory positional
#parameters (i.e., positional parameters lacking defaults) on the passed
#callable should also be trivial, because they *MUST* strictly correspond to
#the first n child type hints of the first argument of the expected parent
#"typing.Callable" type hint. It's optional positional parameters and keyword
#arguments that are the rub. *shrug*
#
#Obviously, we'll want to dynamically generate the full test based on the
#expected parent "typing.Callable" type hint. For sanity, do this iteratively
#by generating code testing arbitrary "__annotations__" against a "Callable"
#type hint (in increasing order of complexity):
#* Passed *NO* parameters and returning something typed.
#* Passed *ONE* parameter and returning something typed.
#* Passed *TWO* parameters and returning something typed.
#* Passed an arbitrary number of parameters and returning something typed.
#
#Note that test should ideally avoid iteration. We're fairly certain we can do
#that by mapping various attributes from the code object of the passed callable
#into something that enables us to produce a tuple of type hints matching the
#first argument of the expected parent "Callable" type hint.
#
#*BINGO!* The value of the "func.__code__.co_varnames" attribute is a tuple of
#both parameter names *AND* local variables. Fortunately, the parameter names
#come first. Unfortunately, there are two types: standard and keyword-only.
#Altogether, an expression yielding a tuple of the names of all parameters
#(excluding local variables) is given by:
#
#    #FIXME: Insufficient. Variadic parameters also exist. Also, note that this
#    #has already been efficiently implemented as get_func_arg_names()!
#    func_codeobj = get_func_unwrapped_codeobj(func)
#
#    # Tuple of the names of all parameters accepted by this callable.
#    func_param_names = func_codeobj.co_varnames[
#        :func_codeobj.co_argcount + func_codeobj.co_kwonlyargcount]
#
#Note that "func_param_names" probably excludes variadic positional and keyword
#argument names, but that's probably fine, because "Callable" type hint syntax
#doesn't appear to explicitly support that sort of thing anyway. I mean, how
#would it? Probably using the "..." singleton ellipse object, I'm sure. But
#that's completely undefined, so it seems doubtful anyone's actually doing it.
#
#We then need to use that tuple to slice "func.__annotations__". Of course, you
#can't slice a dictionary in Python, because Python dictionaries are much less
#useful than they should be. See also:
#    https://stackoverflow.com/questions/29216889/slicing-a-dictionary
#
#The simplest and fastest approach we can currently think of is given by:
#    func_param_name_to_hint = func.__annotations__
#
#    # Generator comprehension producing type hints for this callable's
#    # parameters in the same order expected by the first argument of the
#    # "Callable" type hint.
#    func_param_hints = (
#        func_param_name_to_hint[func_param_name]
#        for func_param_name in func_param_names
#    )
#
#Note that because we know the exact number of expected parameters up front
#(i.e., as the len() of the first argument of the "Callable" type hint), we can
#generate optimal code *WITHOUT* a generator or other comprehension and thus
#*WITHOUT* iteration. Yes, this is literally loop unrolling in Python, which is
#both hilarious and exactly what CPython developers get for failing to support
#generally useful operations on dictionaries and sets: e.g.,
#
#    callable_type_hint = ... # Give this a name for reference below.
#
#    # Number of non-variadic parameters expected to be accepted by this
#    # caller-passed callable.
#    FUNC_PARAM_LEN_EXPECTED = len(callable_type_hint[0])
#
#    # Generator comprehension producing type hints for this callable's
#    # parameters in the same order expected by the first argument of the
#    # "Callable" type hint.
#    func_param_hints = (
#        func_param_name_to_hint[func_param_names[0]],
#        func_param_name_to_hint[func_param_names[1]],
#        ...
#        func_param_name_to_hint[func_param_names[FUNC_PARAM_LEN_EXPECTED]],
#    )
#
#Clearly, there's *LOADS* of additional preliminary validation that needs to
#happen here as well. Since "Callable" type hint syntax *REQUIRES* a return
#type hint to be specified (yes, this is absolutely non-optional), we also need
#to ensure that "func_param_name_to_hint" contains the 'return' key.
#
#Given all that, the final test would then resemble something like:
#
#    (
#        __beartype_pith_n_func_param_name_to_hint := (
#            func.__annotations__ or LOOKUP_IN_TYPESHED_SOMEHOW) and
#        'return' in __beartype_pith_n_func_param_name_to_hint and
#        __beartype_pith_n_func_codeobj := getattr(
#            __beartype_pith_n, '__code__', None) and
#        # Just ignore C-based callables and assume they're valid. Unsure what
#        # else we can do with them. Okay, we could also proxy them here, but
#        # that seems a bit lame. Just accept them as is for now, perhaps?
#        __beartype_pith_n_func_codeobj is None or (
#            __beartype_pith_n_func_param_names := (
#                __beartype_pith_n_func_codeobj.co_varnames) and
#            len(__beartype_pith_n_func_param_names) == {FUNC_PARAM_LEN_EXPECTED} and
#            (
#                __beartype_pith_n_func_param_name_to_hint[__beartype_pith_n_func_param_names[0]],
#                __beartype_pith_n_func_param_name_to_hint[__beartype_pith_n_func_param_names[1]],
#                ...
#                __beartype_pith_n_func_param_name_to_hint[__beartype_pith_n_func_param_names[FUNC_PARAM_LEN_EXPECTED]],
#                __beartype_pith_n_func_param_name_to_hint['return']
#            ) == {callable_type_hint}
#        )
#    )
#
#*YUP.* That's super hot, that is. We're sweating.
#
#Note this test is effectively O(1) but really O(FUNC_PARAM_LEN_EXPECTED) where
#FUNC_PARAM_LEN_EXPECTED is sufficiently small that it's basically O(1). That
#said, the constant factors are non-negligible. Fortunately, callables *NEVER*
#change once declared. You should now be thinking what we're thinking:
#*CACHING*. That's right. Just stuff the results of the above test (i.e., a
#boolean) into our duffel LRU cache keyed on the fully-qualified name of that
#callable. We only want to pay the above price once per callable, if we can
#help it, which we absolutely can, so let's do that please.
#
#*NOTE THAT ASSIGNMENT EXPRESSIONS ARE EFFECTIVELY MANDATORY.* I mean, there's
#basically no way we can avoid them, so let's just require them. By the time we
#get here anyway, Python 3.6 will be obsolete, which just leaves Python 3.7. We
#could just emit warnings when decorating callables annotated by "Callable"
#type hints under Python 3.7. </insert_shrug>
#
#*NOTE THAT BUILTINS DO NOT HAVE CODE OBJECTS,* complicating matters. At this
#point, we could care less, but we'll have to care sometime that is not now.
#FIXME: *OH.* Note that things are slightly less trivial than detailed above.
#It's not enough for a callable to be annotated, of course; that callable also
#needs to be annotated *AND* type-checked by a runtime type checker like
#@beartype or @typeguard. The same, of course, does *NOT* apply to "typeshed"
#annotations, because we generally expect stdlib callables to do exactly what
#they say and nothing more or less. This means the above approach should only
#be employed as a last-ditch fallback in the event that the passed callable
#does *NOT* satisfy any of the following:
#* Is decorated by a runtime type checker *AND* has a non-None
#  "__annotations__" dictionary.
#* Is annotated by the third-party optional "typeshed" dependency.
#
#Trivial, but worth noting.
#FIXME: Lastly, note that everywhere we say "typeshed" above, we *REALLY* mean
#a PEP 561-compliant search for stub files annotating that callable.
#Unsurprisingly, the search algorithm is non-trivial, which will impact the
#performance gains associated with type-checking annotations in the first
#place. Ergo, we might consider omitting aspects of this search that are both
#highly inefficient *AND* unlikely to yield positive hits. See also:
#    https://www.python.org/dev/peps/pep-0561/

#FIXME: *IT'S CONFIGURATION TIME.* So, let's talk about how we efficiently
#handle @beartype configuration like the "is_proxying" boolean introduced
#above. It's worth getting this right the first time. Happily, we got this
#right the first time with a balls-crazy scheme that gives us O(1)
#configurability that supports global defaults that can be both trivially
#changed globally *AND* overridden by passed optional @beartype parameters.
#
#Note this scheme does *NOT* require us to litter the codebase with cumbersome
#and inefficient logic like:
#    muh_setting = (
#        beartype_params.muh_setting if beartype_params.muh_setting is not None else
#        beartype._global_config.muh_setting)
#
#What is this magic we speak of? *SIMPLE.* We twist class variable MRO lookup
#in our favour. Since CPython already efficiently implements such lookup with a
#fast C implementation, we can hijack that implementation for our own sordid
#purposes to do something completely different. Note that only *CLASS* variable
#MRO lookup suffices. Since classes are global singletons, all subclasses will
#implicitly perform efficient lookups for undefined class variables in their
#superclass -- which is exactly what we want and need here.
#
#Specifically:
#* Define a new private "beartype._config" submodule.
#* In that submodule:
#  * Define a new public "BeartypeConfigGlobal" class declaring all
#    configuration settings as class variables defaulting to their desired
#    arbitrary global defaults: e.g.,
#        class BeartypeConfigGlobal(object):
#            '''
#            **Global beartype configuration.**
#            '''
#
#            is_proxying = True
#            ...
#* Publicly expose that class to external users as a new public
#  "beartype.config" *PSEUDO-MODULE.* In reality, that object will simply be an
#  alias of "beartype._config.BeartypeConfigGlobal". But users shouldn't know
#  that. They should just treat that object as if it was a module. To effect
#  this, just establish this alias in the "beartype.__init__" submodule: e.g.,
#      from beartype._config import BeartypeConfigGlobal
#
#      # It really is that simple, folks. Maybe. Gods, let it be that simple.
#      config = BeartypeConfigGlobal
#* Privatize the existing public "beartype._decor.decormain" submodule to a new
#  "beartype._decor._template" submodule.
#* In that submodule:
#  * Rename the existing @beartype decorator to beartype_template(). That
#    function will now only be called internally rather than externally.
#* Define a new private "beartype._decor.decorcache" submodule.
#* In that submodule:
#  * Define a new "BEARTYPE_PARAMS_TO_DECOR" dictionary mapping from a *TUPLE*
#    of positional arguments listed in the exact same order as the optional
#    parameters accepted by the new @beartype decorator discussed below to
#    subclasses to dynamically generated @beartype decorators configured by
#    those subclasses. This tuple should just literally be the argument tuple
#    passed to the @beartype decorator, which is probably easiest to achieve if
#    we force @beartype parameters to be passed as keyword-only arguments:
#
#        # Keyword-only arguments require Python >= 3.8. Under older Pythons,
#        # just drop the "*". Under older Pythons, let's just *NOT ALLOW
#        # CONFIGURATION AT ALL.* So, this gives us:
#        if IS_PYTHON_AT_LEAST_3_8:
#            def beartype(*, is_proxying: bool = None, ...) -> Callable:
#                BEARTYPE_PARAMS = (is_proxying, ...)
#
#                beartype_decor = BEARTYPE_PARAMS_TO_DECOR.get(BEARTYPE_PARAMS)
#                if beartype_decor:
#                    return beartype_decor
#
#                # Else, we need to make a new @beartype decorator passed
#                # these parameters, cache that decorator in
#                # "BEARTYPE_PARAMS_TO_DECOR", and return that decorator.
#        else:
#            # Probably not quite right, but close enough.
#            beartype = beartype_template
#
#    We need a hashable tuple for lookup purposes. That's *ABSOLUTELY* the
#    fastest way, given that we expect keyword arguments. So, we're moving on.
#    Also, do *NOT* bother with LRU caching here, as the expected size of that
#    dictionary will almost certainly always be less than 10 and surely 100.
#* Define a new private "beartype._decor.decormain" submodule.
#* In that submodule:
#  * Define a new @beartype decorator accepting *ALL* of the *EXACT* same
#    class variables declared by the "BeartypeConfigGlobal" class as optional
#    parameters of the same name but *UNCONDITIONALLY* defaulting to "None".
#    That last bit is critical. Do *NOT* default them to what the
#    "BeartypeConfigGlobal" superclass defaults them to, as that would obstruct
#    our purposes, which is to have lookups punted upward to the
#    "BeartypeConfigGlobal" superclass only when undefined in a subclass.
#  * The purpose of this new @beartype decorator is to (in order):
#    * First lookup the passed parameters to get an existing decorator passed
#      those parameters, as already implemented above. (This is trivial.)
#    * If we need to make a new decorator, this is also mostly trivial. Just:
#      * Define a new local dictionary "BEARTYPE_PARAM_NAME_TO_VALUE" bundling
#        these optional parameters for efficient lookup: e.g.,
#            BEARTYPE_PARAM_NAME_TO_VALUE = {
#                'is_proxying': is_proxying,
#                ...
#            }
#      * Dynamically create a new "BeartypeConfigGlobal" subclass *SETTING THE
#        DESIRED CLASS VARIABLES* based on all of the passed optional
#        parameters whose values are *NOT* "None". For example, if the only
#        passed non-"None" optional parameter was "is_proxying", this would be:
#            class _BeartypeConfigDecor{ARBITRARY_NUMBER}(BeartypeConfigGlobal):
#                is_proxying = False
#        This will probably require a bit of iteration to filter out all
#        non-"None" optional parameters. Note that the simplest way to
#        implement this would probably be to just dynamically declare an empty
#        subclass and then monkey-patch that subclass' dictionary with the
#        desired non-"None" optional parameters: e.g.,
#            # Pseudo-code, but close enough.
#            BeartypeConfigDecor = eval(
#                f'''class _BeartypeConfigDecor{ARBITRARY_NUMBER}(BeartypeConfigGlobal): pass''')
#
#            # Yes, this is a bit lame, but it suffices for now. Remember,
#            # we're caching this class, so the logic constructing this class
#            # doesn't need to be lightning fast. It's *FAR* more critical that
#            # the logic looking up this class in this class be lightning fast.
#            #
#            # Do *NOT* try to embed this logic into the above evaluation
#            # (e.g., as f-expressions). Yes, that sort of hackery is trivial
#            # with booleans but rapidly gets hairy with containers. So, I
#            # *GUESS* we could do that for booleans. Just remember that that
#            # doesn't generalize to the general case. Actually, don't bother.
#            # The following suffices and doesn't violate DRY, which is the
#            # only important thing here.
#            BeartypeConfigDecor.__dict__.update({
#                arg_name: arg_value
#                arg_name, arg_value in BEARTYPE_PARAM_NAME_TO_VALUE.items()
#                if arg_value is not None
#            })
#      * Dynamically *COPY* the beartype_template() function into a new
#        function specific to that subclass, which means that function is
#        actually just a template. We'll never actually the original function
#        itself; we just use that function as the basis for dynamically
#        generating new decorators on-the-fly. Heh! Fortunately, we only need
#        a shallow function copy. That is to say, we want the code objects to
#        remain the same. Note that the most efficient means of implementing
#        this is given directly be this StackOverflow answer:
#            https://stackoverflow.com/a/13503277/2809027
#        Note that that answer can be slightly improved to resemble:
#            WRAPPER_ASSIGNMENTS = functools.WRAPPER_ASSIGNMENTS + ('__kwdefaults__',)
#            def copy_func(f):
#                g = types.FunctionType(f.__code__, f.__globals__, name=f.__name__,
#                                       argdefs=f.__defaults__,
#                                       closure=f.__closure__)
#                g = functools.update_wrapper(g, f, WRAPPER_ASSIGNMENTS)
#                return g
#        That's the most general form. Of course, we don't particularly care
#        about copying metadata, since we don't expect anyone to care about
#        these dynamically generated decorators. That means we can reduce the
#        above to simply:
#            def copy_func(f):
#                return types.FunctionType(
#                    f.__code__,
#                    f.__globals__,
#                    name=f.__name__,
#                    argdefs=f.__defaults__,
#                    closure=f.__closure__,
#                )
#      * Monkey-patch the new decorator returned by
#        "copy_func(beartype_template)" with the new subclass: e.g.,
#            beartype_decor = copy_func(beartype_template)
#            beartype_decor.__beartype_config = BeartypeConfigDecor
#        *HMMM.* Minor snag. That doesn't work, but the beartype_template()
#        template won't have access to that "__beartype_config". Instead, we'll
#        need to:
#        * Augment the signature of the beartype_template() template to accept
#          a new optional "config" parameter default to "None": e.g.,.
#          def beartype_template(
#              func: Callable, config: BeartypeConfigGlobal = None) -> Callable:
#        * Either refactor the copy_func() function defined above to accept a
#          caller-defined "argdefs" parameter *OR* (more reasonably) just
#          inline the body of that function in @beartype as:
#            beartype_decor = types.FunctionType(
#                f.__code__,
#                f.__globals__,
#                name=f.__name__,
#                # Yup. In theory, that should do it, if we recall the internal
#                # data structure of this parameter correctly.
#                argdefs=(BeartypeConfigDecor,),
#                closure=f.__closure__,
#            )
#      * Cache and return that decorator:
#            BEARTYPE_PARAMS_TO_DECOR[BEARTYPE_PARAMS] = beartype_decor
#            return beartype_decor
#
#Pretty trivial, honestly. We've basically already implemented all of the hard
#stuff above, which is nice.
#
#Note that the beartype_template() function will now accept an optional
#"config" parameter -- which will, of course, *ALWAYS* be non-"None" by the
#logic above. Assert this, of course. We can then trivially expose that
#"config" to lower-level beartype functions by just stuffing it into the
#existing "BeartypeCall" class: e.g.,
#    # Welp, that was trivial.
#    func_data.config = config
#
#Since we pass "func_data" everywhere, we get configuration for free. Muhaha!

#FIXME: Propagate generic subscriptions both to *AND* from pseudo-superclasses.
#First, consider the simpler case of propagating a generic subscription to
#pseudo-superclasses: e.g.,
#    from typing import List
#    class MuhList(List): pass
#
#    @beartype
#    def muh_lister(muh_list: MuhList[int]) -> None: pass
#
#During internal type hint visitation, @beartype should propagate the "int"
#child type hint subscripting the "MuhList" type hint up to the "List"
#pseudo-superclass under Python >= 3.9. Under older Python versions, leaving
#"List" unsubscripted appears to raise exceptions at parse time. *shrug*
#
#Of the two cases, this first case is *SIGNIFICANTLY* more important than the
#second case documented below. Why? Because mypy (probably) supports this first
#but *NOT* second case, for  which mypy explicitly raises an "error". Since
#mypy has effectively defined the standard interpretation of type hints,
#there's little profit in contravening that ad-hoc standard by supporting
#something unsupported under mypy -- especially because doing so would then
#expose end user codebases to mypy errors. Sure, that's "not our problem, man,"
#but it kind of is, because community standards exist for a reason -- even if
#they're ad-hoc community standards we politely disagree with.
#
#Nonetheless, here's the second case. Consider the reverse case of propagating
#a generic subscription from a pseudo-superclass down to its unsubscripted
#generic: e.g.,
#    from typing import Generic, TypeVar
#
#    T = TypeVar('T')
#    class MuhGeneric(Generic[T]):
#        def __init__(self, muh_param: T): pass
#
#    @beartype
#    def muh_genericizer(generic: MuhGeneric, T) -> None: pass
#
#During internal type hint visitation, @beartype should propagate the "T"
#child type hint subscripting the "Generic" pseudo-superclass down to the
#"MuhGeneric" type hint under Python >= 3.9 and possibly older versions. Doing
#so would reduce DRY violations, because there's no tangible reason why users
#should have to perpetually subscript "MuhGeneric" when its pseudo-superclass
#already has been. Of course, mypy doesn't see it that way. *shrug*

#FIXME: When time permits, we can augment the pretty lame approach by
#publishing our own "BeartypeDict" class that supports efficient random access
#of both keys and values. Note that:
#* The existing third-party "randomdict" package provides baseline logic that
#  *MIGHT* be useful in getting "BeartypeDict" off the ground. The issue with
#  "randomdict", however, is that it internally leverages a "list", which
#  probably then constrains key-value pair deletions on the exterior
#  "randomdict" object to an O(n) rather than O(1) operation, which is
#  absolutely unacceptable.
#* StackOverflow questions provide a number of solutions that appear to be
#  entirely O(1), but which require maintaining considerably more internal data
#  structures, which is also unacceptable (albeit less so), due to increased
#  space consumption that probably grows unacceptable fast and thus fails to
#  generally scale.
#* Since we don't control "typing", we'll also need to augment "BeartypeDict"
#  with a "__class_getitem__" dunder method (or whatever that is called) to
#  enable that class to be subscripted with "typing"-style types ala:
#     def muh_func(muh_mapping: BeartypeDict[str, int]) -> None: pass
#In short, we'll need to conduct considerably more research here.
#FIXME: Actually, none of the above is necessary or desirable. Rather than
#designing a random access "BeartypeDict" class, it would be *FAR* more useful
#to design a series of beartype-specific container types in a new external
#"beartypes" package, each of which performs O(1) type-checking *ON INSERTION
#OF EACH CONTAINER ITEM.* This should be stupidly fast under standard use
#cases, because we typically expect an item to be inserted only once but
#accessed many, many times. By just checking on insertion, we avoid *ALL* of
#the complications of trying to type-check after the fact during sequential
#non-random iteration over items.
#
#Indeed, there appears to be a number of similar projects with the same idea,
#with the caveat that these projects *ALL* leverage package-specific constructs
#rather than PEP-compliant type hints -- a significant negative. The most
#interesting of these are:
#* "typed_python", a fascinating package with a variety of novel ideas at play.
#  In addition to providing package-specific container types that perform
#  PEP-noncompliant type-checking on item insertion *IMPLEMENTED THAT AT THE C
#  LEVEL* rather than in pure Python (which is both horrible and fascinating,
#  mainly because... why bother? I mean, PyPy, Nuitka, and Cython already
#  exist, so why go to all that trouble to work in C rather than Python?),
#  this package also offers:
#  * "typed_python.Entrypoint", which looks balls-cray-cray. This is probably
#    the most interesting aspect of this package, presuming it actually behaves
#    as advertised, which it almost certainly doesn't. Nonetheless, it appears
#    to be a bit of a cross between Nuitka and beartype. To quote:
#    "Simply stick the @typed_python.Entrypoint decorator around any function
#     that uses "typed_python" primitives to get a fast version of it:
#     @Entrypoint
#     def sum(someList, zero):
#         for x in someList:
#             zero += x
#         return x
#     ...will generate specialized code for different data types
#     ("ListOf(int)", say, or "ListOf(float)", or even "Dict(int)") that's not
#     only many times faster than the python equivalent, but that can operate
#     using multiple processors. Compilation occurs each time you call the
#     method with a new combination of types." The "that can operate using
#     multiple processors" part is particularly novel, as it implies
#     circumvention of the GIL. "typed_python" appears to implement this magic
#     by leveraging LLVM to compile Python down to C. Again, we strongly doubt
#     any of this actually works under real-world industrial constraints, but
#     it's still a fascinating thought experiment.
#  * "type_python.Class", a generic-style class one subclasses to generate
#    "strongly typed class with a packed memory layout." The "strongly typed"
#    part isn't terribly interesting, as it's PEP-noncompliant. The "packed
#    memory layout" part, however, *IS* interesting. Reducing space consumption
#    by presumably compiling to C is intriguing, if tangential to our concerns.
