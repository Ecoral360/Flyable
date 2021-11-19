from __future__ import annotations
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from flyable.data.lang_func import LangFunc
    from flyable.data.attribut import Attribut

import ast

import flyable.data.lang_file as lang_file
from flyable.data.lang_type import LangType
import flyable.data.lang_class_type as class_type


class LangClass:

    def __init__(self, node: ast.AST):

        self.__node: ast.AST = node
        self.__funcs: list[LangFunc] = []
        self.__attributes: list[Attribut] = []
        self.__id: int = -1
        self.__struct = None
        self.__file: Union[lang_file.LangFile, None] = None
        self.__inherits: list[LangClass] = []
        self.__class_type = class_type.LangClassType()

    def get_node(self):
        return self.__node

    def set_file(self, file):
        self.__file = file

    def get_file(self):
        return self.__file

    def add_func(self, func):
        func.set_class(self)
        func.set_id(len(self.__funcs))
        self.__funcs.append(func)

    def get_func(self, index: Union[str, int]):
        """
        Deprecated: 
            you should call `get_func_by_idx` or `get_func_by_name` instead
        """
        return self.get_func_by_id(index) if isinstance(index, int) else self.get_func_by_name(index)

    def get_func_by_name(self, name: str):
        """Get the function with the matching name or
        None if there isn't one

        Args:
            name (str): the name of the function

        Returns:
            Union[LangFile, None]: The function with the matching name, 
            or None if there isn't one
        """
        for e in self.__funcs:
            if e.get_name() == name:
                return e

    def get_func_by_id(self, idx: int):
        """Get the function at the specified index

        Args:
            idx (int): the index of the function

        Returns:
            Union[LangFile, None]: The function at specified index, or None if the index is not in bound
        """
        # the `- 1` in `abs(idx) - 1` is necessary because if we have a list of length n and want
        # to access the 0th element with negative idx, it will be index -n but the abs(-n) == n
        # and it wouldn't pass the test abs(idx) < len(list) if one wasn't substracted from it
        return self.__funcs[idx] if abs(idx) - 1 < len(self.__funcs) else None

    def funcs_iter(self):
        return iter(self.__funcs)

    def set_id(self, id: int):
        self.__id = id

    def get_id(self):
        return self.__id

    def get_name(self) -> str:
        return self.__node.name   # type: ignore

    def add_attribute(self, attr):
        attr.set_id(len(self.__attributes))
        self.__attributes.append(attr)

    def get_attribute(self, index):
        if isinstance(index, int):
            return self.__attributes[index]
        elif isinstance(index, str):
            for e in self.__attributes:
                if e.get_name() == index:
                    return e
        return None

    def get_attributes_count(self):
        return len(self.__attributes)

    def attributes_iter(self):
        return iter(self.__attributes)

    def add_inherit(self, inherit: LangClass):
        self.__inherits.append(inherit)

    def iter_inherits(self):
        return iter(self.__inherits)

    def get_inherits(self, index: int):
        return self.__inherits[index]

    def set_struct(self, struct):
        self.__struct = struct

    def get_struct(self):
        return self.__struct

    def get_lang_type(self):
        return LangType(LangType.Type.OBJECT, self.__id)

    def get_class_type(self):
        return self.__class_type

    def clear_info(self):
        self.__class_type = class_type.LangClassType()
        for func in self.__funcs:
            func.clear_info()
