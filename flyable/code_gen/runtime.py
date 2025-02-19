from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flyable.code_gen.code_builder import CodeBuilder
    from flyable.code_gen.code_gen import CodeGen
    from flyable.data.lang_type import LangType

import flyable.code_gen.code_gen as _code_gen
import flyable.code_gen.code_type as code_type
import flyable.code_gen.debug as debug
import flyable.data.lang_type as lang_type
import flyable.data.type_hint as type_hint
import flyable.code_gen.ref_counter as ref_counter

from flyable.code_gen.code_type import CodeType

"""
Module to call runtimes functions
"""


def create_bytes_object(code_gen: CodeGen, builder: CodeBuilder, byte_str: bytes):
    str_ptr = builder.ptr_cast(builder.global_str(byte_str.decode('utf-8')), code_type.get_int8_ptr())
    pybytes_from_object = code_gen.get_or_create_func("PyBytes_FromString",
                                                      code_type.get_py_obj_ptr(code_gen),
                                                      [CodeType(CodeType.CodePrimitive.INT8).get_ptr_to()],
                                                      _code_gen.Linkage.EXTERNAL)
    return builder.call(pybytes_from_object, [str_ptr])


def create_unicode(code_gen: CodeGen, builder: CodeBuilder, str: int):
    """
    Generate an external call to the python function to create a string
    """
    from_string = code_gen.get_or_create_func("PyUnicode_FromString",
                                              CodeType(CodeType.CodePrimitive.INT8).get_ptr_to(),
                                              [CodeType(CodeType.CodePrimitive.INT8).get_ptr_to()])
    return builder.call(from_string, [str])


def pydict_getitem(code_gen: CodeGen, builder: CodeBuilder, d: int, k: int):
    """
    Get value associated with key from the dictionary
    """
    return_type = code_type.get_py_obj_ptr(code_gen)
    args_types = [code_type.get_py_obj_ptr(code_gen), code_type.get_py_obj_ptr(code_gen)]
    func = code_gen.get_or_create_func("PyDict_GetItem", return_type, args_types, _code_gen.Linkage.EXTERNAL)
    return builder.call(func, [d, k])


def malloc_call(code_gen: CodeGen, builder: CodeBuilder, value_size: int):
    """
    Generate an external call to the Python runtime memory allocator
    """
    malloc_func = code_gen.get_or_create_func("PyMem_Malloc", code_type.get_py_obj_ptr(code_gen),
                                              [CodeType(CodeType.CodePrimitive.INT64)], _code_gen.Linkage.EXTERNAL)
    return builder.call(malloc_func, [value_size])


def free_call(code_gen: CodeGen, builder: CodeBuilder, memory_to_free: int):
    free_func = code_gen.get_or_create_func("PyMem_Free", code_type.get_void(), [code_type.get_int8_ptr()],
                                            _code_gen.Linkage.EXTERNAL)
    memory_to_free = builder.ptr_cast(memory_to_free, code_type.get_int8_ptr())
    return builder.call(free_func, [memory_to_free])


def py_runtime_get_string(code_gen: CodeGen, builder: CodeBuilder, value: str):
    str_ptr = builder.ptr_cast(builder.global_str(value), code_type.get_int8_ptr())
    args_type = [code_type.get_int8_ptr(), code_type.get_int64()]
    new_str_func = code_gen.get_or_create_func("PyUnicode_FromStringAndSize", code_type.get_py_obj_ptr(code_gen),
                                               args_type, _code_gen.Linkage.EXTERNAL)
    return builder.call(new_str_func, [str_ptr, builder.const_int64(len(value))])


def py_runtime_init(code_gen: CodeGen, builder: CodeBuilder):
    init_func = code_gen.get_or_create_func("Py_Initialize", code_type.get_void(), [], _code_gen.Linkage.EXTERNAL)
    return builder.call(init_func, [])


def value_to_pyobj(visitor, value: int, value_type: LangType):
    code_gen = visitor.get_code_gen()
    builder = visitor.get_builder()
    result_type = lang_type.get_python_obj_type()

    if value_type.is_int():

        int_const_hint = type_hint.get_lang_type_contained_hint_type(value_type, type_hint.TypeHintConstInt)

        if int_const_hint is None:
            py_func = code_gen.get_or_create_func("PyLong_FromLongLong", code_type.get_py_obj_ptr(code_gen),
                                                  [CodeType(CodeType.CodePrimitive.INT64)], _code_gen.Linkage.EXTERNAL)
            result_type.add_hint(type_hint.TypeHintRefIncr())
            return result_type, builder.call(py_func, [value])
        else:
            return result_type, builder.load(
                builder.global_var(code_gen.get_or_insert_const(int_const_hint.get_value())))
    elif value_type.is_dec():
        dec_const_hint = type_hint.get_lang_type_contained_hint_type(value_type, type_hint.TypeHintConstDec)
        if dec_const_hint is None:
            result_type.add_hint(type_hint.TypeHintRefIncr())
            py_func = code_gen.get_or_create_func("PyFloat_FromDouble", code_type.get_py_obj_ptr(code_gen),
                                                  [code_type.get_double()], _code_gen.Linkage.EXTERNAL)
            return result_type, builder.call(py_func, [value])
        else:
            return result_type, builder.load(
                builder.global_var(code_gen.get_or_insert_const(dec_const_hint.get_value())))
    elif value_type.is_bool():
        true_block = builder.create_block("Convert bool True")
        false_block = builder.create_block("Convert bool false")
        continue_block = builder.create_block("Convert bool continue")

        bool_alloca = visitor.generate_entry_block_var(code_type.get_py_obj_ptr(code_gen))
        builder.cond_br(value, true_block, false_block)

        builder.set_insert_block(true_block)
        true_var = builder.global_var(code_gen.get_true())
        builder.store(true_var, bool_alloca)
        builder.br(continue_block)

        builder.set_insert_block(false_block)
        false_var = builder.global_var(code_gen.get_false())
        builder.store(false_var, bool_alloca)
        builder.br(continue_block)

        builder.set_insert_block(continue_block)
        result = builder.load(bool_alloca)
        ref_counter.ref_incr(builder, lang_type.get_python_obj_type(), result)
        result_type.add_hint(type_hint.TypeHintRefIncr())
        return result_type, result
    elif value_type.is_none():
        none_value = builder.global_var(code_gen.get_none())
        ref_counter.ref_incr(builder, lang_type.get_python_obj_type(), none_value)
        return result_type, none_value
    elif value_type.is_obj() or value_type.is_collection():
        # Make sure the object is of python objet ptr to keep consistent types
        if type_hint.is_incremented_type(value_type):  # Keep the incremental hint
            result_type.add_hint(type_hint.TypeHintRefIncr())
        return result_type, builder.ptr_cast(value, code_type.get_py_obj_ptr(code_gen))

    return result_type, value
