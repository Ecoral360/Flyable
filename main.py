"""
Here is an example on how to use Flyable.
You need to have the GCC compiler in your PATH.

The process in divided in 3 parts.
Compiling : Read and transform the Python into machines instructions contained inside an object file.
Linking : Combine the generated object file with Python runtime to generate an executable program.
Running : Run the generated program. Generated exe file will try to find an existing python installation on the setup.
"""

import platform
from pathlib import Path
from subprocess import PIPE, Popen

import flyable.compiler as com
import flyable.tool.platform as plat
from flyable.tool.utils import Step, end_step, start_step


def main(file: str, output_dir: str = ".", exec_name: str = "a"):
    start_step("Compiling")

    compiler = com.Compiler()
    compiler.add_file(file)
    compiler.set_output_path(f"{output_dir}/output.o")
    # Make sur the folder exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    compiler.compile()

    end_step()

    if compiler.has_error():
        return

    # Link the object file
    start_step("Linking")

    # Now link the code
    python_lib = "python310.lib" if platform.system() == "Windows" else "python3.10.a"
    linker_args = ["gcc", "-flto", "output.o", "libFlyableRuntime.a", python_lib]
    p = Popen(linker_args, cwd=output_dir)
    p.wait()
    if p.returncode != 0:
        raise Exception("Linking error")

    end_step()


def run_code(output_dir: str, exec_name: str):
    """Runs the code

    Args:
        output_dir (str): the directory where the code is
        exec_name (str): the name of the executable
    """
    start_step("Running")
    p = Popen(
        [output_dir + f"/{exec_name}.exe"], cwd=output_dir, stdin=PIPE, stdout=PIPE
    )
    output, err = p.communicate()
    end_step()

    print("-------------------")
    print(output.decode())  # Print what the program outputted

    print("Application ended with code " + str(p.returncode))


if __name__ == "__main__":
    dir = f"./build3/{plat.get_platform_folder()}"
    main("test.py", dir, "a")
    # run_code(dir, "a")
