# Configuration Scripts for Nobara Linux - My Dots!

This repository contains a set of Python scripts designed to automate the configuration of my Nobara Linux systems. These scripts handle tasks such as package management, repository configuration, and system cleanup.

## Overview

The scripts are organized within a Python package structure (`Configuration/Nobara/`). This structure allows for modularity and easier maintenance.

## Directory Structure

```
Configuration/
├── Nobara/
│   ├── __init__.py
│   ├── cleanup.py
│   ├── general.py
│   ├── repos/
│   │   ├── __init__.py
│   │   └── terra.py
│   └── ... other modules ...
├── __init__.py
├── install.sh
└── README.md
```

*   `Configuration/`: The root directory of the Python package.
*   `Nobara/`:  A subpackage containing Nobara-specific scripts.
*   `__init__.py`:  Empty files that designate directories as Python packages.
*   `cleanup.py`: Script for removing unnecessary packages.
*   `general.py`:  Script for general system configuration tasks.
*   `repos/`: Subpackage for managing repositories.
*   `terra.py`: Example script related to a specific repository (Terra).
*   `install.sh`:  Installation script to set up the environment and dependencies.
*   `README.md`: This file, providing documentation for the project.


## Installation

1.  Clone the repository:

    ```bash
    git clone <https://github.com/v1mkss/.dotsfiles.git>
    cd <repository_directory>
    ```

2.  Run the installation script:

    ```bash
    ./install.sh
    ```

    The `install.sh` script sets the `PYTHONPATH` environment variable and installs any necessary dependencies. Ensure that `PYTHONPATH` is correctly set to the project root directory for proper module import resolution.

## Contributing

Contributions are welcome!  If you have improvements or bug fixes, please submit a pull request.

## License

This project is licensed under the [MIT] License.
