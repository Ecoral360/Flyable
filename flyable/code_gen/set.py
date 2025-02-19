"""
Module routine to handle set
"""
from __future__ import annotations
from typing import TYPE_CHECKING
import flyable.code_gen.code_gen as gen
import flyable.code_gen.code_type as code_type

if TYPE_CHECKING:
    from flyable.parse.parser import ParserVisitor


def instanciate_python_set(visitor: ParserVisitor, obj: int):
    """
    Generate the code to allocate a Python Set
    """
    builder = visitor.get_builder()
    code_gen = visitor.get_code_gen()
    new_set_args_types = [code_type.get_py_obj_ptr(code_gen)]
    new_set_func = code_gen.get_or_create_func("PySet_New", code_type.get_py_obj_ptr(code_gen),
                                                new_set_args_types, gen.Linkage.EXTERNAL)
    return builder.call(new_set_func, [obj])


def python_set_add(visitor: ParserVisitor, set_obj: int, item: int):
    """
    Generate the code to set an element in a Python Set
    """
    builder = visitor.get_builder()
    code_gen = visitor.get_code_gen()
    set_item_args_types = [code_type.get_py_obj_ptr(code_gen), code_type.get_py_obj_ptr(code_gen)]
    set_item_func = code_gen.get_or_create_func("PySet_Add", code_type.get_int32(),
                                                set_item_args_types, gen.Linkage.EXTERNAL)
    return builder.call(set_item_func, [set_obj, item])


def python_set_len(visitor: ParserVisitor, set_obj: int):
    """
    Generate the code that returns the len of the Set
    """
    builder = visitor.get_builder()
    code_gen = visitor.get_code_gen()
    args_types = [code_type.get_py_obj_ptr(code_gen)]
    list_len_func = code_gen.get_or_create_func("PySet_Size", code_type.get_int64(), args_types, gen.Linkage.EXTERNAL)
    return builder.call(list_len_func, [set_obj])
