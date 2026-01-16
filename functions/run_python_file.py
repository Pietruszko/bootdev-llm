import os
import subprocess


def run_python_file(working_directory, file_path, args=None):
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_dir = os.path.normpath(os.path.join(working_dir_abs, file_path))
        valid_target_dir = os.path.commonpath([working_dir_abs, target_dir]) == working_dir_abs
        if not valid_target_dir:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        if not os.path.isfile(target_dir):
            return f'Error: "{file_path}" does not exist or is not a regular file'
        if not str(file_path).endswith(".py"):
            return f'Error: "{file_path}" is not a Python file'

        command = ["python", target_dir]

        if args:
            command.extend(args)

        sub_proces = subprocess.run(command, cwd=working_dir_abs, capture_output=True, text=True, timeout=30)
        output = []
        if sub_proces.returncode != 0:
            output.append(f"Process exited with code {sub_proces.returncode}")
        if not sub_proces.stderr and not sub_proces.stdout:
            output.append("No output produced")
        else:
            output.append(f"STDOUT: {sub_proces.stdout}" if sub_proces.stdout else "")
            output.append(f"STDERR: {sub_proces.stderr}" if sub_proces.stderr else "")

        return "\n".join(output)

    except Exception as e:
        return f"Error: executing Python file: {e}"
