import os
import sys
import subprocess
import configparser
import shutil
import argparse

def log_info(message):
    """Logs an informational message to standard output."""
    print(f"INFO: {message}")

def log_error(message):
    """Logs an error message to standard error and exits."""
    print(f"ERROR: {message}", file=sys.stderr)

# Check if the script is run through install.sh by looking for the environment variable
if not os.environ.get("DOTFILES_INSTALLATION"):
    log_error("This script must be run through install.sh")
    sys.exit(1)

# Get the Python binary from the environment (set by install.sh)
PYTHON_BIN = os.environ.get("PYTHON_BIN")
if not PYTHON_BIN:
    log_error("PYTHON_BIN environment variable not set. This script must be run through install.sh")
    sys.exit(1)

# Get no_sys state from environment (set by install.sh)
NO_SYS = os.environ.get("NO_SYS", "false").lower() == "true"


# Removed detect_distribution and install_python_dependencies


def setup_python():
    """Checks for python3 and returns its binary path.
       Assumes python has been installed by install.sh."""
    python_bin = shutil.which("python3") or shutil.which("python")
    if not python_bin:
         # This should ideally not happen if install.sh ran correctly
         log_error("Python binary not found. Ensure install.sh installed Python correctly.")
         sys.exit(1)

    try:
        python_version = subprocess.check_output([python_bin, '--version'], text=True).strip()
        log_info(f"Using Python: {python_version}")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
         log_error(f"Could not verify Python installation: {e}")
         sys.exit(1)

    return python_bin


def copy_user_configs(user_config_dir, no_bak):
    """Copies user configuration files, handling git config specially."""
    home_dir = os.environ.get("SUDO_USER_HOME") or os.environ.get("HOME")
    if not home_dir:
        log_error("Could not determine user's home directory.")
        sys.exit(1)
    config_dir_dest = os.path.join(home_dir, ".config")

    # Ensure destination config directory exists
    if not os.path.exists(config_dir_dest):
        try:
            os.makedirs(config_dir_dest)
            log_info(f"Created directory: {config_dir_dest}")
        except OSError as e:
            log_error(f"Error creating directory {config_dir_dest}: {e}")
            sys.exit(1)

    # Handle git config specially
    dotfiles_git_config = os.path.join(user_config_dir, "git", "config")
    user_git_config_dir = os.path.join(config_dir_dest, "git")
    user_git_config = os.path.join(user_git_config_dir, "config")
    user_git_config_bak = os.path.join(user_git_config_dir, "config.bak")

    # Ensure the destination git config directory exists
    if not os.path.exists(user_git_config_dir):
        try:
            os.makedirs(user_git_config_dir)
            log_info(f"Created directory: {user_git_config_dir}")
        except OSError as e:
            log_error(f"Error creating directory {user_git_config_dir}: {e}")
            sys.exit(1)

    # Backup the existing git config, if it exists
    if os.path.isfile(user_git_config):
        log_info(f"Existing git config found at {user_git_config}.")
        if not no_bak:
            log_info(f"Backing up {user_git_config} to {user_git_config_bak}")
            try:
                shutil.copy2(user_git_config, user_git_config_bak)
                # log_info("Backup successful.") # Removed this log
                pass
            except IOError as e:
                log_error(f"Error backing up {user_git_config}: {e}")
                # Decide if this is a fatal error or just warn
                pass # Continue installation even if backup fails
    else:
        log_info(f"No existing git config found.")


    # Extract [user], [tag], and [commit] sections from backup
    extracted_content = []
    in_target_section = False
    target_sections = {"[user]", "[tag]", "[commit]"} # Use a set for faster lookup

    if os.path.exists(user_git_config_bak):
         log_info(f"Extracting specific sections from backup {user_git_config_bak}")
         try:
            with open(user_git_config_bak, "r") as f_bak:
                for line in f_bak:
                    stripped_line = line.strip()
                    if stripped_line.startswith("[") and stripped_line.endswith("]"):
                        # It's a section header
                        if stripped_line in target_sections:
                            in_target_section = True
                            extracted_content.append(line) # Keep original line with newline
                            # log_info(f"  Extracted section header: {stripped_line}") # Removed this log
                            pass
                        else:
                            in_target_section = False
                    elif in_target_section:
                        # It's content within a target section
                        extracted_content.append(line)
                        # Optional: log each line extracted
                        # log_info(f"  Extracted line: {stripped_line}")
         except IOError as e:
             log_error(f"Error reading backup file {user_git_config_bak}: {e}")
         # log_info(f"Extraction complete. {len(extracted_content)} lines extracted.") # Removed this log
         pass


    # Overwrite destination with new config from dotfiles, creating if it does not exist
    log_info(f"Overwriting/Creating {user_git_config} with new config from {dotfiles_git_config}")
    try:
        shutil.copy2(dotfiles_git_config, user_git_config)
        # log_info("Overwrite/Create successful.") # Removed this log
        pass
    except IOError as e:
        log_error(f"Error overwriting/creating {user_git_config}: {e}")
        # If overwrite fails, exit
        sys.exit(1)

    # Append extracted content
    if extracted_content:
        log_info(f"Appending extracted sections to {user_git_config}")
        try:
            with open(user_git_config, "a") as f_user:
                f_user.writelines(extracted_content)
            # log_info("Append successful.") # Removed this log
            pass
        except IOError as e:
            log_error(f"Error appending to {user_git_config}: {e}")
            pass # Continue even if appending fails


    # Copy the rest of the user config files (excluding git)
    log_info(f"Copying remaining user config files from {user_config_dir} to {config_dir_dest}...")
    if os.path.isdir(user_config_dir):
         for item in os.listdir(user_config_dir):
             s = os.path.join(user_config_dir, item)
             d = os.path.join(config_dir_dest, item)
             # Skip the git directory as it was handled
             if os.path.basename(s) == "git":
                 log_info(f"Skipping git config directory: {s}")
                 continue

             try:
                 if os.path.isdir(s):
                     log_info(f"Copying directory {s} to {d}")
                     # Use dirs_exist_ok=True for recursive copy
                     shutil.copytree(s, d, dirs_exist_ok=True)
                 elif os.path.isfile(s):
                     log_info(f"Copying file {s} to {d}")
                     shutil.copy2(s, d) # Use copy2 to preserve metadata
             except Exception as e:
                 log_error(f"Error copying {s} to {d}: {e}")
    else:
        log_info(f"User config directory not found: {user_config_dir}")

    log_info(f"Finished copying user config contents.")


def run_patches(user_patches_dir):
    """Runs Python patch scripts, excluding the git merge script."""
    log_info(f"Running patches from {user_patches_dir}...")
    # Get the Python binary from the environment
    python_bin = os.environ.get("PYTHON_BIN")
    if not python_bin:
        log_error("PYTHON_BIN environment variable not set. Cannot run patches.")
        return # Do not exit, just skip patches

    home_dir = os.environ.get("SUDO_USER_HOME") or os.environ.get("HOME")
    if not home_dir:
        log_error("Could not determine user's home directory. Cannot run patches.")
        return

    if os.path.isdir(user_patches_dir):
        for filename in os.listdir(user_patches_dir):
            patch = os.path.join(user_patches_dir, filename)
            # Exclude the old merge_git_config.py script and ensure it's a python file
            if os.path.isfile(patch) and filename != "merge_git_config.py" and patch.lower().endswith(".py"):
                log_info(f"Running patch: {patch}")
                try:
                    # Use the determined python_bin
                    subprocess.check_call([python_bin, patch])
                except subprocess.CalledProcessError as e:
                    log_error(f"Error running patch {patch}: {e}")
    else:
        log_info(f"User patches directory not found: {user_patches_dir}")
    log_info("Finished running patches.")


def copy_system_files(system_files_dir, no_bak):
    """Copies system files with optional backup, requires sudo."""
    # Use the NO_SYS global variable set from the environment
    if NO_SYS:
        log_info("--no-sys option provided, skipping system files")
        return
    if not os.path.isdir(system_files_dir):
        log_info(f"System files directory not found: {system_files_dir}")
        return

    log_info("Copying system files...")
    # Walk through the source system files directory
    for root, _, files in os.walk(system_files_dir):
        for filename in files:
            src_path = os.path.join(root, filename)
            # Get the relative path from the system_files_dir
            rel_path = os.path.relpath(src_path, system_files_dir)
            # Construct the destination path starting from the root (/)
            dest_path = os.path.join("/", rel_path)

            # Ensure parent directory exists for system files
            dest_parent_dir = os.path.dirname(dest_path)
            if not os.path.exists(dest_parent_dir):
                 log_info(f"Creating system directory: {dest_parent_dir}")
                 try:
                     # Use sudo for creating directories in system paths
                     subprocess.check_call(["sudo", "mkdir", "-p", dest_parent_dir])
                     log_info("Directory created.")
                 except subprocess.CalledProcessError as e:
                     log_error(f"Error creating system directory {dest_parent_dir}: {e}")
                     continue # Skip this file if directory creation fails


            if os.path.exists(dest_path) and not no_bak:
                backup_path = dest_path + ".bak"
                log_info(f"Backing up {dest_path} to {backup_path}")
                try:
                    # Use sudo for backing up system files
                    subprocess.check_call(["sudo", "cp", "-f", dest_path, backup_path])
                    log_info("Backup successful.")
                except subprocess.CalledProcessError as e:
                    log_error(f"Error backing up {dest_path}: {e}")
                    pass # Continue to copying even if backup fails


            log_info(f"Copying {src_path} to {dest_path}")
            try:
                # Use sudo for copying to system paths
                subprocess.check_call(["sudo", "cp", src_path, dest_path])
                log_info("Copy successful.")
            except subprocess.CalledProcessError as e:
                log_error(f"Error copying {src_path} to {dest_path}: {e}")

    log_info("Finished copying system files.")


if __name__ == "__main__":
    # Argument parsing
    parser = argparse.ArgumentParser(description="Dotfiles installer")
    parser.add_argument("--no-bak", action="store_true", help="Skip backups")
    # --no-sys is now handled primarily by install.sh based on distro detection,
    # but we keep it here for direct script execution if needed for testing,
    # or if install.sh passes it explicitly. The environment variable is preferred.
    parser.add_argument("--no-sys", action="store_true", help="Skip system configs")
    args = parser.parse_args()

    # Use parsed arguments
    no_bak = args.no_bak
    # Use the NO_SYS global variable which is set from the environment or argparse
    # no_sys = args.no_sys # This line is removed, use the global NO_SYS

    # Define constant directories relative to the script's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    user_config_dir = os.path.join(script_dir, "user", ".config")
    user_patches_dir = os.path.join(script_dir, "user", "patches")
    system_files_dir = os.path.join(script_dir, "system")

    # Distro detection and Python setup are now handled by install.sh

    # Perform installation steps
    copy_user_configs(user_config_dir, no_bak) # Removed python_bin arg
    run_patches(user_patches_dir) # Removed python_bin arg
    copy_system_files(system_files_dir, no_bak) # Removed no_sys arg, uses global NO_SYS

    log_info("Dotfiles installation complete.")
