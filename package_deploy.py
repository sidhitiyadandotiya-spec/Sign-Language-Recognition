import argparse
import os
from pathlib import Path
import zipfile


PROJECT_DIR = Path(__file__).resolve().parent
EXCLUDED_DIRS = {".git", "__MACOSX", "__pycache__", "user_data"}
EXCLUDED_FILES = {".DS_Store", "users.json"}
MAX_ARCHIVE_PATH_LENGTH = 240


def should_exclude(relative_path: Path) -> bool:
    parts = relative_path.parts
    if any(part in EXCLUDED_DIRS for part in parts):
        return True
    if any(part.startswith(".venv") for part in parts):
        return True
    return relative_path.name in EXCLUDED_FILES or relative_path.name.startswith("._")


def build_deployment_archive(output_path: Path) -> int:
    output_path = output_path.resolve()
    files = []
    long_paths = []

    for current_dir, directories, filenames in os.walk(PROJECT_DIR):
        current_path = Path(current_dir)
        directories[:] = [
            name
            for name in directories
            if not should_exclude((current_path / name).relative_to(PROJECT_DIR))
        ]
        for filename in filenames:
            source_path = current_path / filename
            if source_path.resolve() == output_path:
                continue
            relative_path = source_path.relative_to(PROJECT_DIR)
            if should_exclude(relative_path):
                continue

            archive_path = Path(PROJECT_DIR.name) / relative_path
            archive_name = archive_path.as_posix()
            if len(archive_name) > MAX_ARCHIVE_PATH_LENGTH:
                long_paths.append(archive_name)
            files.append((source_path, archive_name))

    if long_paths:
        raise ValueError(
            "Deployment archive contains paths longer than "
            f"{MAX_ARCHIVE_PATH_LENGTH} characters: {long_paths[:5]}"
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(
        output_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6
    ) as archive:
        for source_path, archive_name in files:
            archive.write(source_path, archive_name)

    with zipfile.ZipFile(output_path, "r") as archive:
        corrupt_member = archive.testzip()
        if corrupt_member is not None:
            raise RuntimeError(f"Deployment archive failed validation at {corrupt_member}")

    return len(files)


def main() -> None:
    default_output = PROJECT_DIR.parent / f"{PROJECT_DIR.name}_deploy.zip"
    parser = argparse.ArgumentParser(
        description="Build a clean deployment archive without virtualenvs or local user data."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=default_output,
        help=f"Output ZIP path (default: {default_output})",
    )
    args = parser.parse_args()

    file_count = build_deployment_archive(args.output)
    print(f"Created and verified {args.output.resolve()} ({file_count} files).")


if __name__ == "__main__":
    main()
