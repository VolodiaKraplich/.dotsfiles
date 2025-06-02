import os
import sys
import re # Using regex for more robust line matching

def log_info(message):
    """Logs an informational message."""
    print(f"INFO (fastfetch_logo_patch.py): {message}")

def log_error(message):
    """Logs an error message and indicates failure."""
    print(f"ERROR (fastfetch_logo_patch.py): {message}", file=sys.stderr)

def read_file_lines(file_path):
    """Reads a file into a list of lines."""
    lines = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        log_error(f"Config file not found: {file_path}")
        return None
    except IOError as e:
        log_error(f"Error reading file {file_path}: {e}")
        return None
    return lines

def write_lines_to_file(file_path, lines):
    """Writes a list of lines back to a file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
    except IOError as e:
        log_error(f"Error writing to file {file_path}: {e}")
        return False
    return True

# Function to parse /etc/os-release
def parse_os_release(file_path="/etc/os-release"):
    """Parses ID and ID_LIKE from /etc/os-release."""
    info = {}
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line:
                        key, value = line.split('=', 1)
                        # Remove surrounding quotes and convert to lowercase
                        info[key.lower()] = value.strip('"').strip("'").lower()
        except IOError as e:
            log_error(f"Error reading '{file_path}': {e}")
        except Exception as e:
             log_error(f"Error parsing '{file_path}': {e}")
    return info


# --- Script execution starts here ---

# Determine the user's home directory dynamically
# This script is expected to be run by install.sh, which sets SUDO_USER_HOME or relies on HOME
user_home = os.environ.get("SUDO_USER_HOME") or os.environ.get("HOME")
if not user_home:
    log_error("Could not determine user's home directory from environment.")
    sys.exit(1) # Indicate failure

config_file = os.path.join(user_home, ".config", "fastfetch", "config.jsonc")

# Detect distribution ID and like
# Prioritize environment variables (set by install.sh), then fall back to /etc/os-release
env_distro_id = os.environ.get("DISTRO_ID", "").lower()
env_distro_like = os.environ.get("DISTRO_LIKE", "").lower()

distro_id = env_distro_id
distro_like = env_distro_like

log_info(f"Attempting detection. Env DISTRO_ID: '{os.environ.get('DISTRO_ID', '<not set>')}', Env DISTRO_LIKE: '{os.environ.get('DISTRO_LIKE', '<not set>')}'")

# If environment variables are not fully set, try /etc/os-release
if not distro_id or not distro_like:
    log_info("Environment variables not fully set, attempting to read /etc/os-release.")
    os_release_info = parse_os_release()

    if not distro_id and 'id' in os_release_info:
        distro_id = os_release_info['id']
        log_info(f"Set DISTRO_ID from os-release: '{distro_id}'")
    if not distro_like and 'id_like' in os_release_info:
        distro_like = os_release_info['id_like']
        log_info(f"Set DISTRO_LIKE from os-release: '{distro_like}'")

log_info(f"Final detected DISTRO_ID: '{distro_id}', DISTRO_LIKE: '{distro_like}'")

# Map distribution IDs and likes to Fastfetch logo sources
# Prioritize DISTRO_ID, then check DISTRO_LIKE
logo_map = {
    "nobara": "fedora_small",
    "fedora": "fedora_small",
    "arch": "arch_small",
    "cachyos": "cachyos_small",
    "debian": "debian_small",
    "ubuntu": "ubuntu_small",
    "linuxmint": "linuxmint_small",
    "opensuse-leap": "opensuse_small",
    "suse": "opensuse_small",
    "manjaro": "manjaro_small",
    "endeavouros": "endeavouros_small",
}

# Determine the target logo source based on detected distro
target_logo_source = None
if distro_id in logo_map:
    target_logo_source = logo_map[distro_id]
    log_info(f"Mapped DISTRO_ID '{distro_id}' to logo source '{target_logo_source}'.")
elif distro_like:
    # Check distro_like if ID doesn't match
    # Split distro_like by spaces or commas if it's a list
    liked_distros = distro_like.replace(',', ' ').split()
    for liked in liked_distros:
         if liked in logo_map:
            target_logo_source = logo_map[liked]
            log_info(f"Mapped DISTRO_LIKE '{distro_like}' (found liked distro '{liked}') to logo source '{target_logo_source}'.")
            break

# If no specific logo mapping found, use 'linux_small' as the default
if not target_logo_source:
    target_logo_source = "linux_small"
    log_info(f"No specific logo mapping found for detected distribution or its base. Using default logo source: '{target_logo_source}'.")

# Read the current config file content
file_lines = read_file_lines(config_file)
if file_lines is None:
    sys.exit(1) # Error reading file, exit

# Find and replace the logo source line within the 'logo' block
modified_lines = []
in_logo_block = False
logo_source_updated = False

# Regex to find the logo block start line, allowing for indentation and potential comments
logo_block_start_re = re.compile(r'^\s*"logo"\s*:\s*{.*?$', re.IGNORECASE)
# Regex to find the source line within the logo block, capturing indentation and trailing comma/comment
source_line_re = re.compile(r'^(\s*)"source"\s*:\s*".*?"(\s*,?\s*.*)$', re.IGNORECASE) # Capture everything after value including comma and comment

for line in file_lines:
    # Check if we are entering the logo block
    if not in_logo_block and logo_block_start_re.search(line):
        in_logo_block = True
        log_info("Entered 'logo' block.")

    # Check if we are currently inside the logo block and the current line is the 'source' line
    if in_logo_block:
        source_match = source_line_re.match(line)
        if source_match:
            # Found the source line within the logo block
            leading_whitespace = source_match.group(1)
            trailing_chars = source_match.group(2) # Includes comma and any trailing content (whitespace, comment)
            new_source_line = f'{leading_whitespace}"source": "{target_logo_source}"{trailing_chars}\n'
            modified_lines.append(new_source_line)
            log_info(f"Updated 'source' line to: {new_source_line.strip()}")
            logo_source_updated = True
            continue # Skip appending the original line

        # Check if we are exiting the logo block
        # This check should happen after processing the 'source' line in case it's the last line in the block
        if line.strip() == '}':
            in_logo_block = False
            log_info("Exited 'logo' block.")


    # Append the original line if it wasn't the source line in the logo block
    modified_lines.append(line)

if not logo_source_updated:
    log_error("Could not find and update the '\"source\": \"...\"' line within the '\"logo\": { ... }' block in the fastfetch config file.")
    sys.exit(1) # Indicate failure

# Write the modified content back to the file
if write_lines_to_file(config_file, modified_lines):
    log_info("Fastfetch config patched successfully.")
    sys.exit(0) # Indicate success
else:
    sys.exit(1) # Error writing file, exit
