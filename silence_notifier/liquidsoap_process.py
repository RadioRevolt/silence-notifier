import warnings

import psutil
import os.path


class LiquidSoapProcess:
    """Class representing one running LiquidSoap process"""

    def __init__(self, script_path):
        self.proc = self._find_ls_process(script_path)

    def is_running(self):
        """Check if the LiquidSoap process we saw when initializing still runs.
        """
        return self.proc.is_running()

    def _find_ls_process(self, script_path: str) -> psutil.Process:
        """Find the LiquidSoap process we are supposed to monitor.

        Args:
            script_path: Absolute path of the LiquidSoap script which is used
                by the LiquidSoap process we want to monitor.

        Returns:
            Instance of psutil.Process which is bond to the LiquidSoap process
            using the provided script_path.

        Raises:
            ValueError if no LiquidSoap instance could be found using
            script_path.
        """
        script_path = os.path.realpath(script_path)
        ls_processes = self._find_all_ls_processes()
        proc_scripts = self._find_scripts(ls_processes)
        abs_scripts = self._make_scripts_absolute(proc_scripts)

        for proc, proc_script in abs_scripts.items():
            if proc_script == script_path:
                return proc
        else:
            raise ValueError(
                "No LiquidSoap instance runs using {}".format(script_path)
            )

    @staticmethod
    def _find_all_ls_processes() -> list:
        """Return list of all LiquidSoap processes."""
        ls_processes = []
        for proc in psutil.process_iter():
            if proc.name() == "liquidsoap":
                ls_processes.append(proc)

        return ls_processes

    @staticmethod
    def _find_scripts(ls_processes: list) -> dict:
        """Return mapping between processes and the script they use."""
        cmds = {proc: proc.cmdline() for proc in ls_processes}

        scripts = dict()

        for proc, args in cmds.items():
            try:
                scripts[proc] = LiquidSoapProcess._find_script_from_args(args)
            except ValueError as e:
                warnings.warn("Could not figure out what script is used for "
                              "the process '{}'".format(proc.cmdline()))
        return scripts

    @staticmethod
    def _find_script_from_args(args: list) -> str:
        """Find the script from the list of arguments of a LiquidSoap process.
        """
        # First, let's try to find the script arg by excluding all options
        non_option_args = [arg for arg in args[1:] if not arg.startswith('-')]
        num_non_option_args = len(non_option_args)
        if num_non_option_args == 0:
            raise ValueError("All arguments are options")
        elif num_non_option_args == 1:
            return non_option_args[0]
        else:
            # Secondly, try to see if any arguments end in .liq
            liqs = [arg for arg in non_option_args if arg.endswith('.liq')]
            if len(liqs) == 1:
                return liqs[0]
            else:
                # Lastly, only look at arguments with path separators in them
                paths = [arg for arg in non_option_args if os.sep in arg]
                if len(paths) == 1:
                    return paths[0]
                elif len(paths) == 0:
                    raise ValueError(
                        "There is not one argument which is alone in ending in "
                        "'.liq' or alone in containing {}. Thus, which argument"
                        " is the script is impossible to determine."
                        .format(os.sep)
                    )

    @staticmethod
    def _make_scripts_absolute(proc_scripts: dict):
        """Return mapping between processes and the absolute path to their script,
        using a mapping between processes and path to their script."""
        abs_proc_scripts = dict()

        for proc, script in proc_scripts.items():
            if os.path.isabs(script):
                abs_proc_scripts[proc] = script
            else:
                proc_cwd = proc.cwd()
                abs_script = os.path.join(proc_cwd, script)
                abs_proc_scripts[proc] = os.path.normpath(abs_script)
        return abs_proc_scripts



