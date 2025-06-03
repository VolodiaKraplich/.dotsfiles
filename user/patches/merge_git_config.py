import os
import sys
import shutil

def log_info(message):
    print(f"INFO: {message}")

def log_error(message):
    print(f"ERROR: {message}", file=sys.stderr)

def extract_git_sections(backup_file_path, target_sections):
    """Extracts specific sections ([user], [tag], [commit]) from a git config file."""
    extracted_content = []
    log_info(f"Extracting specific sections from backup {backup_file_path}")
    try:
        with open(backup_file_path, "r") as f_bak:
            in_target_section = False
            for line in f_bak:
                stripped_line = line.strip()
                if stripped_line.startswith("[") and stripped_line.endswith("]"):
                    # Case-insensitive comparison
                    if stripped_line.lower() in [s.lower() for s in target_sections]:
                        in_target_section = True
                        extracted_content.append(line)
                    else:
                        in_target_section = False
                elif in_target_section:
                    extracted_content.append(line)
    except IOError as e:
        log_error(f"Error reading backup file {backup_file_path}: {e}")
        return None
    return extracted_content

def backup_git_config(existing_config_path, user_git_config_bak, no_bak):
    """Backs up the existing git config file if it exists and no_bak is not set."""
    if os.path.isfile(existing_config_path):
        log_info(f"Existing git config found at {existing_config_path}.")
        if not no_bak:
            log_info(f"Backing up {existing_config_path} to {user_git_config_bak}")
            try:
                shutil.copy2(existing_config_path, user_git_config_bak)
                return True
            except IOError as e:
                log_error(f"Error backing up {existing_config_path}: {e}")
    return False

def overwrite_git_config(dotfiles_git_config, user_git_config):
    """Overwrites the user's git config with the dotfiles git config."""
    if os.path.exists(dotfiles_git_config):
        log_info(f"Overwriting/Creating {user_git_config} with new config from {dotfiles_git_config}")
        try:
            shutil.copy2(dotfiles_git_config, user_git_config)
            log_info("Overwriting successful.")
            return True
        except IOError as e:
            log_error(f"Error overwriting/creating {user_git_config}: {e}")
            return False
    else:
        log_info(f"Dotfiles git config not found at {dotfiles_git_config}. Skipping overwrite.")
        return False

def append_extracted_content(user_git_config, extracted_content):
    """Appends extracted content to the user's git config, preserving indentation."""
    if not extracted_content:
        return True  # No content to append, consider as success

    if os.path.exists(user_git_config):
        log_info(f"Appending {len(extracted_content)} extracted lines to {user_git_config}")
        try:
            with open(user_git_config, "a") as f_user:
                for line in extracted_content:
                    f_user.write(line)
            log_info("Appending successful.")
            return True
        except IOError as e:
            log_error(f"Error appending to {user_git_config}: {e}")
            return False
    else:
        log_error(f"Destination file {user_git_config} does not exist.")
        return False

def handle_git_ignore(new_ignore_path, existing_ignore_path):
    """Handles copying or appending the ignore file."""
    if os.path.exists(new_ignore_path):
        log_info(f"Found new ignore file: {new_ignore_path}")
        if os.path.exists(existing_ignore_path):
            log_info(f"Existing ignore file found, appending to: {existing_ignore_path}")
            try:
                with open(new_ignore_path, "r") as src, open(existing_ignore_path, "a") as dest:
                    shutil.copyfileobj(src, dest)
                log_info("Successfully appended to existing ignore file.")
                return True
            except IOError as e:
                log_error(f"Error appending to existing ignore file: {e}")
                return False
        else:
            log_info(f"No existing ignore file found, copying: {new_ignore_path} to {existing_ignore_path}")
            try:
                shutil.copy2(new_ignore_path, existing_ignore_path)
                log_info("New ignore file copied successfully.")
                return True
            except IOError as e:
                log_error(f"Error copying new ignore file: {e}")
                return False
    else:
        log_info(f"No new ignore file found: {new_ignore_path}")
    return True

def handle_git_config(user_config_dir, config_dir_dest, no_bak):
    """Handles git config: extracts, overwrites, and appends."""
    dotfiles_git_config = os.path.join(user_config_dir, "git", "config")
    user_git_config_dir = os.path.join(config_dir_dest, "git")
    user_git_config = os.path.join(user_git_config_dir, "config")
    user_git_config_bak = os.path.join(user_git_config_dir, "config.bak")
    target_sections = ["[user]", "[tag]", "[commit]"]

    os.makedirs(user_git_config_dir, exist_ok=True)

    existing_config_path = user_git_config
    extracted_content = []
    backed_up = backup_git_config(existing_config_path, user_git_config_bak, no_bak)

    if backed_up:
        log_info(f"Extracting sections from backup {user_git_config_bak}")
        extracted_content = extract_git_sections(user_git_config_bak, target_sections)
        if extracted_content is None:
            extracted_content = []

    overwritten = overwrite_git_config(dotfiles_git_config, user_git_config)

    if backed_up and extracted_content:
        append_success = append_extracted_content(user_git_config, extracted_content)
        if append_success:
            if os.path.exists(user_git_config_bak):
                log_info(f"Removing backup file: {user_git_config_bak}")
                try:
                    os.remove(user_git_config_bak)
                except OSError as e:
                    log_error(f"Error removing backup file {user_git_config_bak}: {e}")
        else:
            log_error("Failed to append extracted content. Backup retained.")
    elif not overwritten and extracted_content:
        if not os.path.exists(user_git_config):
            log_info(f"Creating empty config file: {user_git_config}")
            try:
                with open(user_git_config, 'a'):
                    pass  # Create empty file
                append_success = append_extracted_content(user_git_config, extracted_content)
                if not append_success:
                    log_error("Failed to append to newly created config file.")
            except IOError as e:
                log_error(f"Error creating file {user_git_config}: {e}")
                return False
    return True

if __name__ == "__main__":
    user_home = os.environ.get("SUDO_USER_HOME") or os.environ.get("HOME")
    if not user_home:
        log_error("Could not determine user's home directory.")
        sys.exit(1)

    config_dir = os.path.join(user_home, ".config", "git")
    if not os.path.exists(config_dir):
        try:
            os.makedirs(config_dir)
            log_info(f"Created directory: {config_dir}")
        except OSError as e:
            log_error(f"Error creating directory {config_dir}: {e}")
            sys.exit(1)

    # Paths for git config
    dotfiles_git_dir = os.path.join(os.path.dirname(__file__), "..", "..", ".config", "git")
    new_config_path = os.path.join(dotfiles_git_dir, "config")
    new_ignore_path = os.path.join(dotfiles_git_dir, "ignore")
    existing_config_path = os.path.join(user_home, ".config", "git", "config")
    existing_ignore_path = os.path.join(user_home, ".config", "git", "ignore")

    # Handle ignore file first
    handle_git_ignore(new_ignore_path, existing_ignore_path)

    # Handle git config
    no_bak = False
    handle_git_config(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), ".config"),
        os.path.join(user_home, ".config"),
        no_bak
    )

    sys.exit(0)
