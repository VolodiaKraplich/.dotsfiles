#!/usr/bin/env python3
"""
A robust, idempotent script to format a Helix `languages.toml` file.

This script uses a block-based processing algorithm to intelligently handle the
non-standard TOML format used by Helix. It is designed to solve issues like
split language configurations and orphaned sub-tables.

Key features:
- **Idempotent**: Running this script multiple times on a file will not
  create duplicate headers or change the content after the first run.
- **Intelligent Grouping**: Correctly associates sub-tables (e.g., `[language.debugger]`)
  with their parent language block.
- **Consolidation**: Correctly handles configurations for a single language (like `rust`)
  that are split across multiple blocks, preventing duplication.
- **Sorting**: Sorts all top-level sections (languages, grammars, servers) alphabetically.
- **Clean Output**: Generates a clean, well-formatted TOML output with clear
  section headers.
"""

import sys
import re
from pathlib import Path
from collections import OrderedDict

# --- Configuration ---
INPUT_FILE_NAME = "languages.toml"
BACKUP_FILE_NAME = "languages.toml.bak"

def process_and_sort_toml(content: str) -> str:
    """
    Cleans, groups, consolidates, and sorts TOML configuration blocks.

    Args:
        content: The raw string content of the languages.toml file.

    Returns:
        A formatted string with sorted and grouped blocks.
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
                # This is the key change: if we see a language block that's
                # already been added, we *ignore the block* but update the
                # context. This prevents duplicating the `rust` block.
                if name not in languages:
                    languages[name] = block
                last_lang_name = name
            else: # Malformed block
                other_configs.append(block)
                last_lang_name = None

        elif header.startswith('[language.'):
            # Append sub-table to the last seen language block
            if last_lang_name and last_lang_name in languages:
                languages[last_lang_name] += "\n\n" + block
            else:  # Orphaned block
                other_configs.append(block)
            # This does not reset last_lang_name, allowing multiple sub-tables to be attached

        elif header.startswith('[[grammar]]'):
            match = re.search(name_pattern, block)
            if match:
                name = match.group(1)
                grammars[name] = block # Overwrites duplicates, keeping the last one
            else: # Malformed block
                other_configs.append(block)
            last_lang_name = None # Reset language context

        else:  # Any other top-level table
            other_configs.append(block)
            last_lang_name = None # Reset language context

    # --- Step 4: Sort the consolidated blocks ---
    sorted_languages = [languages[key] for key in sorted(languages.keys())]
    sorted_grammars = [grammars[key] for key in sorted(grammars.keys())]
    # For other configs, sort by the header line itself for stable ordering
    sorted_others = sorted(other_configs, key=lambda b: b.splitlines()[0])

    # --- Step 5: Generate the final formatted string with clean headers ---
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

    # Join all parts with double newlines and ensure a single trailing newline
    return "\n\n".join(output_parts) + "\n"

def main():
    """Main function to run the script."""
    script_dir = Path(__file__).parent
    input_file = script_dir / INPUT_FILE_NAME
    backup_file = script_dir / BACKUP_FILE_NAME

    if not input_file.is_file():
        print(f"❌ Error: Input file not found at '{input_file}'", file=sys.stderr)
        sys.exit(1)

    print(f"🚀 Starting formatting for '{input_file}'...")

    try:
        # --- Read, Process, Write ---
        print("📄 Reading file content...")
        with open(input_file, 'r', encoding='utf-8') as f:
            original_content = f.read()

        print("⚙️ Cleaning, sorting, and formatting content...")
        formatted_content = process_and_sort_toml(original_content)

        print(f"📋 Creating backup at '{backup_file}'...")
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(original_content)

        print(f"💾 Writing formatted content back to '{input_file}'...")
        with open(input_file, 'w', encoding='utf-8') as f:
            f.write(formatted_content)

        print(f"✅ Formatting complete!.")

        # Remove the backup file after writing the formatted content
        if backup_file.is_file():
            backup_file.unlink()
            print(f"🗑️ Backup file '{backup_file.name}' removed.")

    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
