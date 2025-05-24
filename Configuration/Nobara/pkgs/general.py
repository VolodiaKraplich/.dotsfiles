from Configuration.common import log_info, log_error, run_dnf_command
import sys

PACKAGES_TO_ENSURE = [
    "fish",
    "ghostty",
    "btop",
    "eza",
    "cascadia-code-fonts"
]

log_info("Determining which of the required packages are already installed...")

all_installed = run_dnf_command(["list", "installed"], exit_on_error=False)
if all_installed is None:
    log_error("Failed to retrieve installed packages.")
    sys.exit(1)
installed_packages_all = set()
for line in all_installed.splitlines():
    line = line.strip()
    if not line or line.startswith("Installed") or line.startswith("Available"):
        continue
    pkg = line.split()[0]
    installed_packages_all.add(pkg)
packages_to_install = [pkg for pkg in PACKAGES_TO_ENSURE if pkg not in installed_packages_all]
for pkg in PACKAGES_TO_ENSURE:
    if pkg not in packages_to_install:
        log_info(f"{pkg} is already installed.")

if not packages_to_install:
    log_info("All required packages are already installed. No action needed.")
    sys.exit(0)

log_info(f"The following packages will be installed: {' '.join(packages_to_install)}")

result = run_dnf_command(["install", "-y"] + packages_to_install, exit_on_error=False)
if result is not None:
    log_info(f"Packages ({' '.join(packages_to_install)}) successfully installed.")
else:
    log_error(f"Failed to install one or more packages: {' '.join(packages_to_install)}")
    sys.exit(1)

sys.exit(0)
