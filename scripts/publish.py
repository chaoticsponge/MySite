import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def run_step(label, command):
    print(f"\n==> {label}", flush=True)
    result = subprocess.run(command, cwd=ROOT)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main():
    parser = argparse.ArgumentParser(
        description="Prepare generated site files before committing or pushing."
    )
    parser.add_argument(
        "--skip-diff-check",
        action="store_true",
        help="Skip git diff whitespace/error checks.",
    )
    args = parser.parse_args()

    python = sys.executable
    run_step("Update article metadata and blog listing", [python, "scripts/blog_gen.py"])
    run_step("Generate sitemap", [python, "scripts/sitemap_gen.py"])

    if not args.skip_diff_check:
        run_step("Check diff for whitespace errors", ["git", "diff", "--check"])

    print("\nPublish prep complete. Review the diff, then commit and push when ready.")


if __name__ == "__main__":
    main()
