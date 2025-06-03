import os
import sys
import subprocess
import shutil
import argparse

def log_info(message):
    """Logs an informational message to standard output."""
    print(f"INFO: {message}")

def log_error(message):
    """Logs an error message to standard error and exits."""
    print(f"ERROR: {message}", file=sys.stderr)

if not os.environ.get("DOTFILES_INSTALLATION"):
    log_error("This script must be run through install.sh")
    sys.exit(1)

PYTHON_BIN = os.environ.get("PYTHON_BIN")
if not PYTHON_BIN:
    log_error("PYTHON_BIN environment variable not set. This script must be run through install.sh")
    sys.exit(1)

NO_SYS = os.environ.get("NO_SYS", "false").lower() == "true"


def setup_python():
    """Checks for python3 and returns its binary path.
       Assumes python has been installed by install.sh."""
    python_bin = shutil.which("python3") or shutil.which("python")
    if not python_bin:
         log_error("Python binary not found. Ensure install.sh installed Python correctly.")
         sys.exit(1)

    try:
        python_version = subprocess.check_output([python_bin, '--version'], text=True).strip()
        log_info(f"Using Python: {python_version}")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
         log_error(f"Could not verify Python installation: {e}")
         sys.exit(1)

    return python_bin


def _get_user_config_dest():
    """Determines user's home directory and destination .config path."""
    home_dir = os.environ.get("SUDO_USER_HOME") or os.environ.get("HOME")
    if not home_dir:
        log_error("Could not determine user's home directory.")
        sys.exit(1)
    return os.path.join(home_dir, ".config")

def _ensure_dir_exists(directory):
    """Ensures a directory exists, creating it if necessary."""
    if not os.path.exists(directory):
        log_info(f"Creating directory: {directory}")
        try:
            os.makedirs(directory)
        except OSError as e:
            log_error(f"Error creating directory {directory}: {e}")
            sys.exit(1)


def _copy_remaining_configs(source_dir, dest_dir):
    """Copies the remaining config files from source to destination."""
    if os.path.isdir(source_dir):
        for item in os.listdir(source_dir):
            s = os.path.join(source_dir, item)
            d = os.path.join(dest_dir, item)
            try:
                if os.path.isdir(s):
                    log_info(f"Copying directory {s} to {d}")
                    shutil.copytree(s, d, dirs_exist_ok=True)
                elif os.path.isfile(s):
                    log_info(f"Copying file {s} to {d}")
                    shutil.copy2(s, d)
            except Exception as e:
                log_error(f"Error copying {s} to {d}: {e}")
    else:
        log_info(f"User config directory not found: {source_dir}")


def copy_user_configs(user_config_dir, no_bak):
    """Copies user configuration files."""
    config_dir_dest = _get_user_config_dest()
    _ensure_dir_exists(config_dir_dest)
    _copy_remaining_configs(user_config_dir, config_dir_dest)
    log_info("Finished copying user config contents.")


def run_patches(user_patches_dir):
    """Runs Python patch scripts."""
    log_info(f"Running patches from {user_patches_dir}...")
    python_bin = os.environ.get("PYTHON_BIN")
    if not python_bin:
        log_error("PYTHON_BIN environment variable not set. Cannot run patches.")
        return

    home_dir = os.environ.get("SUDO_USER_HOME") or os.environ.get("HOME")
    if not home_dir:
        log_error("Could not determine user's home directory. Cannot run patches.")
        return

    if os.path.isdir(user_patches_dir):
        for filename in os.listdir(user_patches_dir):
            patch = os.path.join(user_patches_dir, filename)
            if os.path.isfile(patch) and patch.lower().endswith(".py"):
                log_info(f"Running patch: {patch}")
                try:
                    subprocess.check_call([python_bin, patch], env=os.environ)
                except subprocess.CalledProcessError as e:
                    log_error(f"Error running patch {patch}: {e}")
    else:
        log_info(f"User patches directory not found: {user_patches_dir}")
    log_info("Finished running patches.")


def copy_system_files(system_files_dir, no_bak):
    """Copies system files with optional backup, requires sudo."""
    if NO_SYS:
        log_info("--no-sys option provided, skipping system files")
        return
    if not os.path.isdir(system_files_dir):
        log_info(f"System files directory not found: {system_files_dir}")
        return

    log_info("Copying system files...")
    for root, _, files in os.walk(system_files_dir):
        for filename in files:
            src_path = os.path.join(root, filename)
            rel_path = os.path.relpath(src_path, system_files_dir)
            dest_path = os.path.join("/", rel_path)

            dest_parent_dir = os.path.dirname(dest_path)
            if not os.path.exists(dest_parent_dir):
                 log_info(f"Creating system directory: {dest_parent_dir}")
                 try:
                     subprocess.check_call(["sudo", "mkdir", "-p", dest_parent_dir])
                     log_info("Directory created.")
                 except subprocess.CalledProcessError as e:
                     log_error(f"Error creating system directory {dest_parent_dir}: {e}")
                     continue


            if os.path.exists(dest_path) and not no_bak:
                backup_path = dest_path + ".bak"
                log_info(f"Backing up {dest_path} to {backup_path}")
                try:
                    subprocess.check_call(["sudo", "cp", "-f", dest_path, backup_path])
                    log_info("Backup successful.")
                except subprocess.CalledProcessError as e:
                    log_error(f"Error backing up {dest_path}: {e}")
                    pass


            log_info(f"Copying {src_path} to {dest_path}")
            try:
                subprocess.check_call(["sudo", "cp", src_path, dest_path])
                log_info("Copy successful.")
            except subprocess.CalledProcessError as e:
                log_error(f"Error copying {src_path} to {dest_path}: {e}")

    log_info("Finished copying system files.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dotfiles installer")
    parser.add_argument("--no-bak", action="store_true", help="Skip backups")
    parser.add_argument("--no-sys", action="store_true", help="Skip system configs")
    args = parser.parse_args()

    no_bak = args.no_bak

    script_dir = os.path.dirname(os.path.abspath(__file__))
    user_config_dir = os.path.join(script_dir, "user", ".config")
    user_patches_dir = os.path.join(script_dir, "user", "patches")
    system_files_dir = os.path.join(script_dir, "system")

    copy_user_configs(user_config_dir, no_bak)
    run_patches(user_patches_dir)
    copy_system_files(system_files_dir, no_bak)

    log_info("Dotfiles installation complete.")
