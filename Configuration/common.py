import sys
import subprocess

def log_info(message):
    print(f"INFO: {message}")

def log_warn(message):
    print(f"WARN: {message}")

def log_error(message):
    print(f"ERROR: {message}", file=sys.stderr)

def is_installed(package_name):
    """
    Check if a package is installed using dnf.
    Returns True if installed, False otherwise.
    """
    try:
        result = subprocess.run(
            ["dnf", "list", "installed", package_name],
            capture_output=True, text=True, check=False
        )
        return result.returncode == 0
    except FileNotFoundError:
        log_error("dnf command not found. Is dnf installed and in your PATH?")
        sys.exit(1)
    except Exception as e:
        log_error(f"An error occurred while checking package installation: {e}")
        sys.exit(1)

def run_dnf_command(args, exit_on_error=True):
    """
    Run a dnf command with sudo and return stdout if successful.
    If exit_on_error is True, exit on failure.
    """
    try:
        result = subprocess.run(
            ["sudo", "dnf"] + args,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            return result.stdout
        else:
            log_error(f"dnf {' '.join(args)} failed.")
            if result.stderr:
                log_error("dnf output (stderr):")
                print(result.stderr, file=sys.stderr)
            if exit_on_error:
                sys.exit(1)
            return None
    except FileNotFoundError:
        log_error("dnf command not found. Is dnf installed and in your PATH?")
        sys.exit(1)
    except Exception as e:
        log_error(f"An error occurred during dnf command: {e}")
        sys.exit(1)

def repoquery_installed(pattern):
    """
    Return a list of installed packages matching the pattern using dnf repoquery.
    """
    try:
        result = subprocess.run(
            ["sudo", "dnf", "repoquery", "--installed", "--quiet", "--queryformat", "%{name}", pattern],
            capture_output=True, text=True, check=False
        )
        if result.returncode == 0:
            pkgs = result.stdout.strip().split('\n')
            return [p for p in pkgs if p]
        return []
    except FileNotFoundError:
        log_error("dnf command not found. Is dnf installed and in your PATH?")
        sys.exit(1)
    except Exception as e:
        log_error(f"An error occurred during repoquery: {e}")
        sys.exit(1)
