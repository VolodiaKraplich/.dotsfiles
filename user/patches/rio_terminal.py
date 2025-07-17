import os
import sys


def log_info(message): print(f"INFO: {message}")


def log_error(message):
    print(f"ERROR: {message}", file=sys.stderr)


# Determine the user's home directory dynamically
user_home = os.environ.get("SUDO_USER_HOME") or os.environ.get("HOME")
if not user_home:
    log_error("Could not determine user's home directory.")
    sys.exit(1)

config_file = os.path.join(user_home, ".config", "kdeglobals")
section = "[General]"
key1 = "TerminalApplication"
value1 = "rio"
key2 = "TerminalService"
value2 = "rio.desktop"

log_info(f"Patching configuration file: {config_file}")

# Ensure the directory exists
config_dir = os.path.dirname(config_file)
if not os.path.exists(config_dir):
    try:
        os.makedirs(config_dir)
        log_info(f"Created directory: {config_dir}")
    except OSError as e:
        log_error(f"Error creating directory {config_dir}: {e}")
        sys.exit(1)


lines = []
try:
    # Read existing content if file exists
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            lines = f.readlines()
except IOError as e:
    log_error(f"Error reading file {config_file}: {e}")
    sys.exit(1)

# Find the [General] section
general_section_index = -1
for i, line in enumerate(lines):
    if line.strip() == section:
        general_section_index = i
        break

# If [General] section doesn't exist, add it at the end
if general_section_index == -1:
    log_info(f"'{section}' section not found, adding it.")
    if lines and not lines[-1].endswith("\n"):
        lines.append("\n")
    lines.append(f"{section}\n")
    general_section_index = len(lines) - 1

# Prepare lines for insertion within the [General] section
insert_index = general_section_index + 1
while insert_index < len(lines) and not lines[insert_index].strip().startswith("["):
    insert_index += 1

# Dictionary to easily check and update keys within the section
current_section_keys = {}
for i in range(general_section_index + 1, insert_index):
    line = lines[i].strip()
    if "=" in line:
        key_val = line.split("=", 1)
        current_section_keys[key_val[0].strip()] = {"index": i, "line": line}

# Update or add key1
if key1 in current_section_keys:
    old_line = current_section_keys[key1]["line"]
    new_line = f"{key1}={value1}\n"
    if old_line.strip() != new_line.strip():
        lines[current_section_keys[key1]["index"]] = new_line
        log_info(f"Updated line: {new_line.strip()}")
    else:
        log_info(f"Key '{key1}' already set correctly.")
else:
    lines.insert(insert_index, f"{key1}={value1}\n")
    log_info(f"Added line: {key1}={value1}")
    insert_index += 1

# Update or add key2
if key2 in current_section_keys and key2 != key1:
    if key2 in current_section_keys:
        old_line = current_section_keys[key2]["line"]
        new_line = f"{key2}={value2}\n"
        if old_line.strip() != new_line.strip():
            lines[current_section_keys[key2]["index"]] = new_line
            log_info(f"Updated line: {new_line.strip()}")
        else:
            log_info(f"Key '{key2}' already set correctly.")
else:
    lines.insert(insert_index, f"{key2}={value2}\n")
    log_info(f"Added line: {key2}={value2}")


# Write the modified content back to the file
try:
    with open(config_file, "w") as f:
        f.writelines(lines)
    log_info("Configuration updated successfully.")
except IOError as e:
    log_error(f"Error writing to file {config_file}: {e}")
    sys.exit(1)

sys.exit(0)
