import sys
from Configuration.common import log_info, repoquery_installed, run_dnf_command, log_error

PACKAGES_TO_REMOVE_PATTERNS = [
    "dragon", "k3b", "kaddressbook", "kaddressbook-libs", "kdeaccessibility*",
    "kdepim-addons", "kdepim-runtime", "kdepim-runtime-libs", "kdiagram",
    "kf5-akonadi-calendar", "kf5-akonadi-mime", "kf5-akonadi-notes", "kf5-akonadi-search",
    "kf5-calendarsupport", "kf5-eventviews", "kf5-incidenceeditor", "kf5-kcalendarcore",
    "kf5-kcalendarutils", "kf5-kdav", "kf5-kidentitymanagement", "kf5-kimap",
    "kf5-kitinerary", "kf5-kldap", "kf5-kmailtransport", "kf5-kmailtransport-akonadi",
    "kf5-kmbox", "kf5-kontactinterface", "kf5-kpimtextedit", "kf5-kpkpass",
    "kf5-kross-core", "kf5-ksmtp", "kf5-ktnef", "kf5-libgravatar", "kf5-libkdepim",
    "kf5-libkleo", "kf5-libksane", "kf5-libksieve", "kf5-mailcommon", "kf5-mailimporter",
    "kf5-mailimporter-akonadi", "kf5-messagelib", "kf5-pimcommon", "kf5-pimcommon-akonadi",
    "kio-gdrive", "kipi-plugins", "kmahjongg", "kmail", "kmail-account-wizard",
    "kmail-libs", "kmines", "kolourpaint", "kolourpaint-libs", "kontact", "kontact-libs",
    "konversation", "korganizer", "korganizer-libs", "kpat", "krdc", "krdc-libs",
    "krfb", "krfb-libs", "krusader", "ktorrent", "kwrite", "libkdegames", "libkgapi",
    "libkmahjongg", "libkmahjongg-data", "libkolabxml", "libphonenumber", "libwinpr",
    "mpage", "pim-data-exporter", "pim-data-exporter-libs", "pim-sieve-editor",
    "plasma-welcome", "qgpgme", "qt5-qtwebengine-freeworld", "qtkeychain-qt5", "scim*",
    "system-config-printer", "system-config-services", "system-config-users", "unoconv",
    "xsane", "xsane-gimp", "abrt-desktop", "plasma-systemmonitor", "kde-connect",
    "neochat", "qrca", "kate", "kgpg", "kmouth", "mediawriter", "pavucontrol-qt",
    "konsole", "elisa-player"
]

log_info("Collecting the list of installed packages for removal...")

installed_packages = set()
for pattern in PACKAGES_TO_REMOVE_PATTERNS:
    pkgs = repoquery_installed(pattern)
    installed_packages.update(pkgs)

unique_packages = sorted(list(installed_packages)) # Sort for consistent output

if not unique_packages:
    log_info("No packages found for removal. Exiting.")
    sys.exit(0)

log_info(f"The following packages will be removed ({len(unique_packages)}):")
for pkg in unique_packages:
    print(f"  {pkg}")

# Remove packages
if unique_packages:
    result = run_dnf_command(["remove", "-y"] + unique_packages, exit_on_error=False)
    if result is not None:
        log_info("Packages removed successfully.")
    else:
        log_error("Failed to remove one or more packages.")
        sys.exit(1)

sys.exit(0)
