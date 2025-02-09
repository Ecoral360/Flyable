"""
Modules to handle Python exception
"""

from __future__ import annotations

import flyable.code_gen.code_type as code_type
import flyable.code_gen.code_gen as gen
import flyable.code_gen.runtime as runtime
import flyable.code_gen.code_gen as _gen
import flyable.data.lang_type as lang_type
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flyable.code_gen.code_builder import CodeBuilder
    from flyable.code_gen.code_gen import CodeGen
    from flyable.parse.parser_visitor import ParserVisitor


def py_runtime_print_error(code_gen: CodeGen, builder: CodeBuilder):
    print_error_func = code_gen.get_or_create_func("PyErr_Print", code_type.get_void(), [], gen.Linkage.EXTERNAL)
    return builder.call(print_error_func, [])


def py_runtime_clear_error(code_gen: CodeGen, builder: CodeBuilder):
    clear_error_func = code_gen.get_or_create_func("PyErr_Clear", code_type.get_void(), [], gen.Linkage.EXTERNAL)
    return builder.call(clear_error_func, [])


def py_runtime_get_excp(code_gen: CodeGen, builder: CodeBuilder):
    get_excp_func = code_gen.get_or_create_func("PyErr_Occurred", code_type.get_py_obj_ptr(code_gen), [],
                                                gen.Linkage.EXTERNAL)
    return builder.call(get_excp_func, [])


def raise_exception(visitor: ParserVisitor, type, value=None):
    code_gen = visitor.get_code_gen()
    builder = visitor.get_builder()
    if value is None:
        value = runtime.py_runtime_get_string(code_gen, builder, "")

    args_type = [code_type.get_py_obj_ptr(visitor.get_code_gen())] * 2
    set_error_func = visitor.get_code_gen().get_or_create_func("PyErr_SetObject", code_type.get_void(), args_type,
                                                               _gen.Linkage.EXTERNAL)

    type = builder.ptr_cast(type, code_type.get_py_obj_ptr(code_gen))
    value = builder.ptr_cast(value, code_type.get_py_obj_ptr(code_gen))

    return builder.call(set_error_func, [type, value])


def raise_index_error(visitor: ParserVisitor):
    builder = visitor.get_builder()
    index = visitor.get_code_gen().get_or_create_global_var("PyExc_IndexError",
                                                            code_type.get_py_obj(visitor.get_code_gen()),
                                                            gen.Linkage.EXTERNAL)
    excp = builder.global_var(index)
    raise_exception(visitor, excp)


def raise_assert_error(visitor: ParserVisitor, obj):
    builder = visitor.get_builder()
    excp = visitor.get_code_gen().get_or_create_global_var("PyExc_AssertionError",
                                                           code_type.get_py_obj(visitor.get_code_gen()),
                                                           gen.Linkage.EXTERNAL)
    excp = builder.global_var(excp)
    raise_exception(visitor, excp)


def check_excp(visitor: ParserVisitor, value_to_check):
    code_gen = visitor.get_code_gen()
    builder = visitor.get_builder()
    no_excp_block = builder.create_block()
    excp_block = builder.create_block()

    has_excp = builder.eq(value_to_check, builder.const_null(code_type.get_py_obj_ptr(code_gen)))

    # If the value is null, it means there is an exception
    builder.cond_br(has_excp, excp_block, no_excp_block)

    builder.set_insert_block(excp_block)
    handle_raised_excp(visitor)

    builder.set_insert_block(no_excp_block)


def handle_raised_excp(visitor: ParserVisitor):
    found_block = visitor.get_except_block()
    if found_block is None:
        visitor.get_builder().ret_null()
    else:
        visitor.get_builder().br(found_block)
