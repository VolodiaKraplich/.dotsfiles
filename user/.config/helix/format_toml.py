#!/usr/bin/env python3
"""
A robust, idempotent script to format Helix TOML configuration files.

This script uses a block-based processing algorithm to intelligently handle the
non-standard TOML format used by Helix. It can format both `languages.toml` and
`config.toml` while preserving key bindings in the config file.

Key features:
- **Multi-file Support**: Handles both languages.toml and config.toml
- **Keybinding Preservation**: Preserves key binding configurations in config.toml
- **Idempotent**: Running this script multiple times will not change the content after the first run
- **Intelligent Grouping**: Correctly associates sub-tables with their parent blocks
- **Consolidation**: Handles split configurations correctly
- **Sorting**: Sorts sections alphabetically (except keybindings)
- **Clean Output**: Generates well-formatted TOML output with clear section headers
"""

import sys
import re
from pathlib import Path
from collections import OrderedDict
from typing import Dict, List, Optional

# --- Configuration ---
SUPPORTED_FILES = {
    "languages.toml": {
        "backup": "languages.toml.bak",
        "sections": ["Languages", "Grammars", "Language Servers & Other Configurations"]
    },
    "config.toml": {
        "backup": "config.toml.bak",
        "sections": ["Editor Configuration", "Theme & UI", "Key Bindings"]
    }
}

def is_keybinding_block(block: str) -> bool:
    """
    Check if a TOML block contains key bindings.

    Args:
        block: A TOML block string

    Returns:
        bool: True if the block contains key bindings
    """
    header = block.splitlines()[0]
    return header.startswith('[keys.') or header == '[keys]'

def process_and_sort_toml(content: str, file_type: str) -> str:
    """
    Cleans, groups, consolidates, and sorts TOML configuration blocks.

    Args:
        content: The raw string content of the TOML file
        file_type: The type of file being processed ('languages.toml' or 'config.toml')

    Returns:
        A formatted string with sorted and grouped blocks
    """
    # --- Step 1: Clean existing headers to ensure idempotency ---
    # This regex removes the section header comments added by this script.
    header_pattern = r'^\s*# =+\n# .*?\n# =+\s*$'
    cleaned_content = re.sub(header_pattern, '', content, flags=re.MULTILINE).strip()

    # --- Step 2: Split content into logical blocks ---
    # The lookahead `(?=...)` splits *before* each header, keeping the header with its block.
    split_regex = r'(?=^\[)'
    blocks = [b.strip() for b in re.split(split_regex, cleaned_content, flags=re.MULTILINE) if b.strip()]

    # --- Step 3: Group blocks by type and context ---
    if file_type == "languages.toml":
        return process_languages_toml(blocks)
    else:  # config.toml
        return process_config_toml(blocks)

def process_languages_toml(blocks: List[str]) -> str:
    """Process languages.toml specific formatting"""
    languages = OrderedDict()
    grammars = OrderedDict()
    other_configs = []

    last_lang_name = None
    name_pattern = r'name\s*=\s*"([^"]+)"'

    for block in blocks:
        header = block.splitlines()[0]

        if header.startswith('[[language]]'):
            match = re.search(name_pattern, block)
            if match:
                name = match.group(1)
                if name not in languages:
                    languages[name] = block
                last_lang_name = name
            else:
                other_configs.append(block)
                last_lang_name = None

        elif header.startswith('[language.'):
            if last_lang_name and last_lang_name in languages:
                languages[last_lang_name] += "\n\n" + block
            else:
                other_configs.append(block)

        elif header.startswith('[[grammar]]'):
            match = re.search(name_pattern, block)
            if match:
                name = match.group(1)
                grammars[name] = block
            else:
                other_configs.append(block)
            last_lang_name = None

        else:
            other_configs.append(block)
            last_lang_name = None

    # Sort the blocks
    sorted_languages = [languages[key] for key in sorted(languages.keys())]
    sorted_grammars = [grammars[key] for key in sorted(grammars.keys())]
    sorted_others = sorted(other_configs, key=lambda b: b.splitlines()[0])

    # Generate output with headers
    output_parts = []
    if sorted_languages:
        output_parts.append(
            "# =============================================================================\n"
            "# Languages\n"
            "# ============================================================================="
        )
        output_parts.append("\n\n".join(sorted_languages))

    if sorted_grammars:
        output_parts.append(
            "# =============================================================================\n"
            "# Grammars\n"
            "# ============================================================================="
        )
        output_parts.append("\n\n".join(sorted_grammars))

    if sorted_others:
        output_parts.append(
            "# =============================================================================\n"
            "# Language Servers & Other Configurations\n"
            "# ============================================================================="
        )
        output_parts.append("\n\n".join(sorted_others))

    return "\n\n".join(output_parts) + "\n"

def process_config_toml(blocks: List[str]) -> str:
    """Process config.toml specific formatting"""
    unsectioned = []
    editor_configs = OrderedDict()
    theme_configs = OrderedDict()
    keybindings = []

    last_section = None

    for block in blocks:
        header = block.splitlines()[0]

        if is_keybinding_block(block):
            keybindings.append(block)
            last_section = None
        elif header.startswith('[theme') or header.startswith('[statusline') or header.startswith('[editor.statusline'):
            name = header[1:-1]  # Remove [ and ]
            theme_configs[name] = block
            last_section = "theme"
        elif header.startswith('[editor.'):
            name = header[1:-1]  # Remove [ and ]
            editor_configs[name] = block
            last_section = "editor"
        elif header.startswith('[editor]'):
            name = "editor"
            editor_configs[name] = block
            last_section = "editor"
        else:
            unsectioned.append(block)
            last_section = None

    output_parts = []

    # Add unsectioned blocks first
    if unsectioned:
        output_parts.append("\n\n".join(unsectioned))

    # Add editor section with sorted blocks
    if editor_configs:
        if output_parts:
            output_parts.append("")
        output_parts.append(
            "# =============================================================================\n"
            "# Editor Configuration\n"
            "# =============================================================================\n"
        )
        sorted_editor = [editor_configs[key] for key in sorted(editor_configs.keys())]
        output_parts.append("\n\n".join(sorted_editor))

    # Add theme section with sorted blocks
    if theme_configs:
        if output_parts:
            output_parts.append("")
        output_parts.append(
            "# =============================================================================\n"
            "# Theme & UI\n"
            "# =============================================================================\n"
        )
        sorted_theme = [theme_configs[key] for key in sorted(theme_configs.keys())]
        output_parts.append("\n\n".join(sorted_theme))

    # Add keybindings in original order
    if keybindings:
        if output_parts:
            output_parts.append("")
        output_parts.append(
            "# =============================================================================\n"
            "# Key Bindings\n"
            "# =============================================================================\n"
        )
        output_parts.append("\n\n".join(keybindings))

    return "\n".join(output_parts) + "\n"

def main():
    """Main function to run the script."""
    script_dir = Path(__file__).parent

    # Process both supported files
    for file_name, config in SUPPORTED_FILES.items():
        input_file = script_dir / file_name
        backup_file = script_dir / config["backup"]

        if not input_file.is_file():
            continue

        print(f"Processing {file_name}...")

        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                original_content = f.read()

            formatted_content = process_and_sort_toml(original_content, file_name)

            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(original_content)

            with open(input_file, 'w', encoding='utf-8') as f:
                f.write(formatted_content)

            if backup_file.is_file():
                backup_file.unlink()

        except Exception as e:
            print(f"Error processing {file_name}: {e}", file=sys.stderr)
            continue

if __name__ == "__main__":
    main()
