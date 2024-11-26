import dis
import inspect


def iterate_instructions(code_object):
    """Delivers the byte-code instructions as a continuous stream.

    Yields `dis.Instruction`. After each code-block (`co_code`), `None` is
    yielded to mark the end of the block and to interrupt the steam.
    """
    # The arg extension the EXTENDED_ARG opcode represents is automatically handled by get_instructions() but the
    # instruction is left in. Get rid of it to make subsequent parsing easier/safer.
    yield from (i for i in dis.get_instructions(code_object) if i.opname != "EXTENDED_ARG")

    yield None

    # For each constant in this code object that is itself a code object,
    # parse this constant in the same manner.
    for constant in code_object.co_consts:
        if inspect.iscode(constant):
            yield from iterate_instructions(constant)
