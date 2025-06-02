import os
import sys
import configparser
import shutil

def log_info(message):
    print(f"INFO: {message}")

def log_error(message):
    print(f"ERROR: {message}", file=sys.stderr)

# Determine the user's home directory dynamically
user_home = os.environ.get("SUDO_USER_HOME") or os.environ.get("HOME")
if not user_home:
    log_error("Could not determine user's home directory.")
    sys.exit(1)

existing_config_path = os.path.join(user_home, ".config", "git", "config")
new_config_path = os.path.join(os.path.dirname(__file__), "..", ".config", "git", "config") # Path relative to the script

if not os.path.exists(new_config_path):
    log_error(f"New config file not found: {new_config_path}")
    sys.exit(1)

# Ensure the .config/git directory exists
config_dir = os.path.join(user_home, ".config", "git")
if not os.path.exists(config_dir):
    try:
        os.makedirs(config_dir)
        log_info(f"Created directory: {config_dir}")
    except OSError as e:
        log_error(f"Error creating directory {config_dir}: {e}")
        sys.exit(1)

if os.path.exists(existing_config_path):
    log_info(f"Merging existing config: {existing_config_path}")

    # Read existing config
    existing_config = configparser.ConfigParser()
    try:
        existing_config.read(existing_config_path)
        log_info("Successfully read existing config.")
        # Log the sections and keys that were read
        for section in existing_config.sections():
            log_info(f"Found section: {section}")
            for key, value in existing_config[section].items():
                log_info(f"  Key: {key} = {value}")
    except configparser.Error as e:
        log_error(f"Error parsing existing config: {e}")
        sys.exit(1)

    # Read new config
    new_config = configparser.ConfigParser()
    try:
        new_config.read(new_config_path)
    except configparser.Error as e:
        log_error(f"Error parsing new config: {e}")
        sys.exit(1)

    # Iterate through sections in the new config
    for section in new_config.sections():
        if section not in existing_config:
            existing_config[section] = {}
            log_info(f"Adding section '{section}'.")
        # Iterate through keys in the section
        for key, value in new_config[section].items():
            if section not in existing_config or key not in existing_config[section]:
                existing_config[section][key] = value
                log_info(f"Adding key '{key}' to section '{section}'.")
            else:
                log_info(f"Key '{key}' already exists in section '{section}', skipping.")

    # Write merged config
    try:
        with open(existing_config_path, "w") as f:
            existing_config.write(f)
        log_info("Merged config written successfully.")
    except IOError as e:
        log_error(f"Error writing merged config: {e}")
        sys.exit(1)
else:
    log_info(f"No existing config found, copying: {new_config_path} to {existing_config_path}")
    try:
        shutil.copy2(new_config_path, existing_config_path)  # copy with metadata
        log_info("New config copied successfully.")
    except IOError as e:
        log_error(f"Error copying new config: {e}")
        sys.exit(1)

sys.exit(0)