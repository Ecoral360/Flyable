from typing import Any
import ast
from flyable.code_gen.code_gen import CodeGen
from flyable.data.comp_data import CompData
from flyable.data.error_thrower import ErrorThrower
from flyable.parse.parser_visitor import ParserVisitor
import flyable.data.lang_func_impl as impl


class Parser(ErrorThrower):

    def __init__(self, data: CompData, code_gen: CodeGen):
        super().__init__()
        self.__data: CompData = data
        self.__code_gen: CodeGen = code_gen

    def parse_func(self, func):
        """
        This function parse the "unknown" implementation.
        It's mostly use to detect parsing errors.
        """
        func_impl = func.get_unknown_impl()
        self.parse_impl(func_impl)

    def parse_impl(self, func_impl: impl.LangFuncImpl):
        if func_impl.is_unknown():
            return

        func_impl.set_parse_status(impl.LangFuncImpl.ParseStatus.STARTED)
        for i, e in enumerate(func_impl.args_iter()):
            new_var = func_impl.get_context().add_var(
                func_impl.get_parent_func().get_arg(i).arg, e)
            new_var.set_is_arg(True)
        vis = ParserVisitor(self, self.__code_gen, func_impl)
        vis.parse()
        func_impl.set_parse_status(impl.LangFuncImpl.ParseStatus.ENDED)

    def get_code_gen(self):
        return self.__code_gen

    def get_data(self):
        return self.__data
