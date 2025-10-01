#!/usr/bin/env python3
"""
Interactive deployment script for claude-code-langchain

Automates the entire deployment pipeline with validation checks and
interactive prompts for safe publishing to PyPI.

Usage:
    pixi run python scripts/deploy.py

    # Or direct:
    python scripts/deploy.py --target pypi
    python scripts/deploy.py --target testpypi
    python scripts/deploy.py --dry-run
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Optional


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print colored header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.END}\n")


def print_step(step: int, text: str):
    """Print step indicator"""
    print(f"{Colors.BLUE}{Colors.BOLD}[Step {step}]{Colors.END} {text}")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


def run_command(cmd: str, check: bool = True) -> tuple[int, str, str]:
    """
    Run shell command and return (returncode, stdout, stderr)

    Args:
        cmd: Command to run
        check: If True, raise error on non-zero exit

    Returns:
        Tuple of (returncode, stdout, stderr)
    """
    print(f"  Running: {Colors.BOLD}{cmd}{Colors.END}")

    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )

    if check and result.returncode != 0:
        print_error(f"Command failed with exit code {result.returncode}")
        print(f"STDERR: {result.stderr}")
        sys.exit(1)

    return result.returncode, result.stdout, result.stderr


def get_version() -> str:
    """Extract version from pyproject.toml"""
    pyproject = Path("pyproject.toml")
    if not pyproject.exists():
        print_error("pyproject.toml not found!")
        sys.exit(1)

    with open(pyproject) as f:
        for line in f:
            if line.startswith("version ="):
                version = line.split("=")[1].strip().strip('"')
                return version

    print_error("Version not found in pyproject.toml")
    sys.exit(1)


def confirm(prompt: str, default: bool = False) -> bool:
    """
    Ask user for confirmation

    Args:
        prompt: Question to ask
        default: Default answer if user just presses Enter

    Returns:
        True if user confirms, False otherwise
    """
    suffix = "[Y/n]" if default else "[y/N]"
    response = input(f"{prompt} {suffix}: ").lower().strip()

    if not response:
        return default

    return response in ['y', 'yes']


def check_git_status():
    """Verify git status is clean"""
    print_step(1, "Checking Git status")

    returncode, stdout, _ = run_command("git status --porcelain", check=False)

    if stdout.strip():
        print_warning("Working directory has uncommitted changes:")
        print(stdout)
        if not confirm("Continue anyway?", default=False):
            print_error("Deployment cancelled")
            sys.exit(1)
    else:
        print_success("Working directory is clean")


def run_quality_checks():
    """Run code quality checks"""
    print_step(2, "Running quality checks")

    checks = [
        ("Format check", "pixi run format-check"),
        ("Lint", "pixi run lint"),
        ("Type check", "pixi run typecheck"),
    ]

    for name, cmd in checks:
        print(f"\n  {name}...")
        returncode, stdout, stderr = run_command(cmd, check=False)

        if returncode != 0:
            print_error(f"{name} failed")
            print(stderr)
            if not confirm("Continue despite check failures?", default=False):
                sys.exit(1)
        else:
            print_success(f"{name} passed")


def run_tests():
    """Run test suite"""
    print_step(3, "Running tests")

    returncode, stdout, stderr = run_command("pixi run test", check=False)

    if returncode != 0:
        print_error("Tests failed")
        print(stderr)
        if not confirm("Continue despite test failures?", default=False):
            sys.exit(1)
    else:
        print_success("All tests passed")


def clean_build():
    """Clean previous build artifacts"""
    print_step(4, "Cleaning build artifacts")
    run_command("pixi run clean-build")
    print_success("Build artifacts cleaned")


def build_package():
    """Build distribution packages"""
    print_step(5, "Building package")
    run_command("pixi run build-package")
    print_success("Package built successfully")

    # Show what was built
    print("\n  Built distributions:")
    run_command("ls -lh dist/")


def validate_package():
    """Validate package with twine"""
    print_step(6, "Validating package")
    run_command("pixi run validate-package")
    print_success("Package validation passed")


def publish_to_testpypi():
    """Publish to TestPyPI"""
    print_step(7, "Publishing to TestPyPI")

    if not confirm("Upload to TestPyPI?", default=True):
        print_warning("Skipping TestPyPI upload")
        return

    run_command("pixi run publish-test")
    print_success("Published to TestPyPI")

    version = get_version()
    print(f"\n  Test installation:")
    print(f"  pip install -i https://test.pypi.org/simple/ claude-code-langchain=={version}")


def publish_to_pypi():
    """Publish to PyPI"""
    print_step(8, "Publishing to PyPI")

    version = get_version()

    print_warning(f"About to publish version {version} to PyPI")
    print_warning("This action CANNOT be undone (versions are immutable)")

    if not confirm("Proceed with PyPI upload?", default=False):
        print_error("PyPI upload cancelled")
        sys.exit(1)

    run_command("pixi run publish-pypi")
    print_success(f"Published version {version} to PyPI!")

    print(f"\n  Installation:")
    print(f"  pip install claude-code-langchain=={version}")
    print(f"\n  PyPI page:")
    print(f"  https://pypi.org/project/claude-code-langchain/{version}/")


def create_git_tag():
    """Create and push git tag"""
    print_step(9, "Creating Git tag")

    version = get_version()
    tag = f"v{version}"

    if not confirm(f"Create and push tag '{tag}'?", default=True):
        print_warning("Skipping tag creation")
        return

    run_command(f"git tag -a {tag} -m 'Release {tag}'")
    run_command(f"git push origin {tag}")
    print_success(f"Tag {tag} created and pushed")


def main():
    """Main deployment pipeline"""
    parser = argparse.ArgumentParser(
        description="Deploy claude-code-langchain package"
    )
    parser.add_argument(
        "--target",
        choices=["testpypi", "pypi", "both"],
        default="both",
        help="Deployment target (default: both)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run checks and build without publishing"
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip test execution (not recommended)"
    )
    parser.add_argument(
        "--skip-checks",
        action="store_true",
        help="Skip quality checks (not recommended)"
    )

    args = parser.parse_args()

    # Print header
    version = get_version()
    print_header(f"Deploying claude-code-langchain v{version}")

    # Pre-deployment checks
    check_git_status()

    if not args.skip_checks:
        run_quality_checks()
    else:
        print_warning("Skipping quality checks (--skip-checks)")

    if not args.skip_tests:
        run_tests()
    else:
        print_warning("Skipping tests (--skip-tests)")

    # Build
    clean_build()
    build_package()
    validate_package()

    if args.dry_run:
        print_header("Dry Run Complete")
        print("Package is ready for deployment but not published")
        print(f"To deploy: python scripts/deploy.py --target pypi")
        sys.exit(0)

    # Publish
    if args.target in ["testpypi", "both"]:
        publish_to_testpypi()

    if args.target in ["pypi", "both"]:
        publish_to_pypi()
        create_git_tag()

    # Success summary
    print_header("Deployment Complete! 🎉")
    print(f"Version {version} successfully deployed")
    print("\nNext steps:")
    print("  1. Create GitHub Release at:")
    print(f"     https://github.com/kapp667/claude-code-sdk-langchain/releases/new")
    print("  2. Monitor PyPI stats:")
    print(f"     https://pypistats.org/packages/claude-code-langchain")
    print("  3. Update conda-forge feedstock (if applicable)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n" + "="*60)
        print_error("Deployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
