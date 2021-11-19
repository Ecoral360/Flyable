from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flyable.data.lang_type import LangType
    from flyable.code_gen.code_gen import CodeGen
    from flyable.data.lang_func import LangFunc
    from flyable.data.comp_data import CompData
    from flyable.parse.parser import Parser


import copy

import flyable.data.lang_func_impl as lang_func_impl

import flyable.data.type_hint as hint


def adapt_call(func_name: str, call_type: LangType, args: list[LangType], comp_data: CompData, parser: Parser, code_gen: CodeGen):
    """
    Handle the logic to make the function call possible.
    If it's a Flyable optimized object, it will specialise a function.
    Also handle Python object but doesn't do anything with it at the moment.
    """
    if call_type.is_obj():
        _class = comp_data.get_class_by_id(call_type.get_id())
        func = _class.get_func_by_name(func_name)
        if func is not None:
            return adapt_func(func, args, comp_data, parser)
    elif call_type.is_python_obj():
        return call_type

    # Any other type doesn't required the class
    return call_type


def adapt_func(func: LangFunc, args: list[LangType], comp_data: CompData, parser: Parser):
    """
    Specialise a function to the given arguments.
    Return an already specialise one if a matching one found.
    """
    if not __validate(func, args):
        return None

    adapted_impl = func.find_impl_by_signature(args)
    if adapted_impl is not None:
        if not adapted_impl.get_parse_status() == lang_func_impl.LangFuncImpl.ParseStatus.ENDED:
            parser.parse_func(func)
    else:  # Need to create a new implementation
        adapted_impl = lang_func_impl.LangFuncImpl()
        for e in args:
            new_arg = copy.deepcopy(e)
            hint.remove_hint_type(new_arg, hint.TypeHintRefIncr)
            adapted_impl.add_arg(e)
        func.add_impl(adapted_impl)
        parser.get_code_gen().gen_func(adapted_impl)
        parser.parse_impl(adapted_impl)

    return adapted_impl


def __validate(func: LangFunc, args: list[LangType]):
    """
    Make sure the function args count is compatible
    """
    min_args = func.get_min_args()
    max_args = func.get_max_args()
    return max_args == -1 or min_args <= len(args) <= max_args
