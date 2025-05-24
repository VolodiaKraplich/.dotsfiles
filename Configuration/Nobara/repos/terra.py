from Configuration.common import log_info, log_warn, log_error, is_installed
import subprocess
import sys
import os
import re

REPO_NAME = "terra"
PACKAGE_NAME = "terra-release"

log_info(f"Checking if package '{PACKAGE_NAME}' is already installed.")
if is_installed(PACKAGE_NAME):
    log_info(f"Package '{PACKAGE_NAME}' is already installed.")
    sys.exit(0)

log_info(f"Checking if repository '{REPO_NAME}' is already configured.")
try:
    result = subprocess.run(
        ["sudo", "dnf", "repolist", "all"],
        capture_output=True, text=True, check=False
    )
    if result.returncode == 0 and re.search(rf"^{REPO_NAME}\s", result.stdout, re.MULTILINE):
        log_info(f"Repository '{REPO_NAME}' is already configured.")
        log_info(f"The repository may have been added manually. Skipping installation of '{PACKAGE_NAME}'.")
        sys.exit(0)
except FileNotFoundError:
    log_error("dnf command not found. Is dnf installed and in your PATH?")
    sys.exit(1)
except Exception as e:
    log_error(f"An error occurred while checking repository configuration: {e}")
    sys.exit(1)

releasever = ""

log_info("Attempting to determine $releasever using dnf config-manager...")
try:
    result = subprocess.run(
        ["dnf", "config-manager", "--dump-variables"],
        capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
         result = subprocess.run(
            ["sudo", "dnf", "config-manager", "--dump-variables"],
            capture_output=True, text=True, check=False
         )

    if result.returncode == 0:
        match = re.search(r"^\s*releasever\s*=\s*['\"]?([^'\"]+)['\"]?", result.stdout, re.MULTILINE)
        if match:
            releasever = match.group(1)
            if '.' in releasever:
                releasever = releasever.split('.')[0]
except FileNotFoundError:
    log_warn("dnf or dnf config-manager command not found. Cannot determine releasever using dnf.")
except Exception as e:
    log_warn(f"An error occurred while trying to get releasever from dnf: {e}")

if not releasever and os.path.exists("/etc/os-release"):
    log_info("Attempting to determine $releasever from /etc/os-release...")
    try:
        with open("/etc/os-release", "r") as f:
            for line in f:
                if line.startswith("VERSION_ID="):
                    version_id = line.strip().split("=")[1].strip('\"')
                    if '.' in version_id:
                        releasever = version_id.split('.')[0]
                    else:
                        releasever = version_id
                    break
    except Exception as e:
        log_warn(f"An error occurred while reading /etc/os-release: {e}")

if not releasever:
    log_error("Failed to automatically determine $releasever.")
    log_error("Please set the $releasever environment variable manually (e.g. export releasever=9) and run the script again, or check your system configuration.")
    sys.exit(1)

log_info(f"Detected $releasever as: {releasever}")

REPO_URL = f"https://repos.fyralabs.com/terra{releasever}"

log_info(f"Installing package '{PACKAGE_NAME}' to configure repository '{REPO_NAME}'...")
log_info(f"URL for temporary repository: {REPO_URL}")

try:
    result = subprocess.run(
        ["sudo", "dnf", "install", "-y", "--nogpgcheck", "--repofrompath", f"{REPO_NAME},{REPO_URL}", PACKAGE_NAME],
        capture_output=True, text=True, check=False
    )

    if result.returncode == 0:
        log_info(f"Package '{PACKAGE_NAME}' and repository '{REPO_NAME}' successfully installed.")
    else:
        log_error(f"Failed to install package '{PACKAGE_NAME}' from '{REPO_URL}'.")
        log_error("Check the URL, the correctness of the $releasever determination, the availability of the package, and the network connection.")
        if result.stderr:
            log_error("dnf output (stderr):")
            print(result.stderr, file=sys.stderr)
        sys.exit(1)
except FileNotFoundError:
    log_error("dnf command not found. Is dnf installed and in your PATH?")
    sys.exit(1)
except Exception as e:
    log_error(f"An error occurred during package installation: {e}")
    sys.exit(1)

sys.exit(0)
