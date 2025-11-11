#!/usr/bin/env python3
"""
huggingface_downloader — mirror files from a Hugging Face repo (optionally a subfolder)
directly from its webpage URL.

Supported URL forms:
  - https://huggingface.co/<owner>/<repo>
  - https://huggingface.co/<owner>/<repo>/tree/<branch>
  - https://huggingface.co/<owner>/<repo>/tree/<branch>/<path/inside>
  - Also works with datasets and spaces:
      https://huggingface.co/datasets/<owner>/<repo>
      https://huggingface.co/spaces/<owner>/<repo>

Examples:
  # Entire repo (defaults to main if /tree not provided)
  python hf_grab.py "https://huggingface.co/acme/awesome-model" ./out

  # Specific branch root
  python hf_grab.py "https://huggingface.co/acme/awesome-model/tree/dev" ./out

  # Subfolder only (just downloads that path)
  python hf_grab.py "https://huggingface.co/acme/awesome-model/tree/main/models/onnx" ./onnx_only

Authentication:
  Private or gated repos require a user access token with at least READ scope.
  Set it via the environment variable HUGGINGFACE_HUB_TOKEN or log in once with:
      huggingface-cli login
  (If you use the provided PowerShell wrapper, it can prompt and set the token
   for the current process automatically.)

Notes:
  - Resumable: repeated runs only fetch missing/corrupted files.
  - Structure-preserving: local layout mirrors the repo.
  - You can further restrict downloads using allow_patterns/ignore_patterns in code.
"""


import argparse
import os
import re
import sys
import inspect
from pathlib import Path
from urllib.parse import urlparse

from huggingface_hub import HfApi, snapshot_download
try:
    from huggingface_hub.errors import HfHubHTTPError
except Exception:
    from huggingface_hub.utils import HfHubHTTPError  # legacy fallback

HF_TREE_REGEX = re.compile(r"^/([^/]+)/([^/]+)/tree/([^/]+)(?:/(.*))?$")
HF_ROOT_REGEX = re.compile(r"^/([^/]+)/([^/]+)$")

def parse_hf_url(url: str):
    """
    Return (repo_id, revision, subfolder, repo_type)
    repo_type inferred from path prefix; default 'model'.
    """
    u = urlparse(url)
    if u.netloc not in {"huggingface.co", "www.huggingface.co"}:
        raise ValueError("URL must be on huggingface.co")

    path = u.path.rstrip("/")
    repo_type = "model"
    if path.startswith("/datasets/"):
        repo_type = "dataset"
        path = path[len("/datasets"):]
    elif path.startswith("/spaces/"):
        repo_type = "space"
        path = path[len("/spaces"):]

    m = HF_TREE_REGEX.match(path)
    if m:
        owner, repo, branch, subfolder = m.groups()
        return f"{owner}/{repo}", branch, (subfolder or "").strip("/"), repo_type

    m2 = HF_ROOT_REGEX.match(path)
    if m2:
        owner, repo = m2.groups()
        return f"{owner}/{repo}", "main", "", repo_type

    raise ValueError(
        "Unrecognized Hugging Face URL format. Expected:\n"
        "  https://huggingface.co/<owner>/<repo>\n"
        "  https://huggingface.co/<owner>/<repo>/tree/<branch>/<optional/subfolder>\n"
        "Optionally prefixed with /datasets/ or /spaces/."
    )

def _build_auth_kwargs(func, token: str):
    """
    Return a dict with the correct auth kwarg for the given function
    (supports both 'token' and legacy 'use_auth_token'; returns {} if none).
    """
    if not token:
        return {}
    params = inspect.signature(func).parameters
    if "token" in params:
        return {"token": token}
    if "use_auth_token" in params:
        return {"use_auth_token": token}
    return {}

def main():
    p = argparse.ArgumentParser(description="Download files from a Hugging Face repo URL.")
    p.add_argument("url", help="Hugging Face web URL (tree or root).")
    p.add_argument("dest", help="Destination folder to download into.")
    p.add_argument("--quiet", action="store_true", help="Less verbose output.")
    args = p.parse_args()

    try:
        repo_id, revision, subfolder, repo_type = parse_hf_url(args.url)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)

    dest = Path(args.dest).expanduser().resolve()
    dest.mkdir(parents=True, exist_ok=True)

    # Limit to subfolder if provided
    allow_patterns = None
    if subfolder:
        allow_patterns = [f"{subfolder}/**", subfolder]

    local_dir_use_symlinks = False
    if not args.quiet:
        scope = f"(subfolder: /{subfolder})" if subfolder else "(whole repo)"
        print(f"Repo:        {repo_id}")
        print(f"Type:        {repo_type}")
        print(f"Revision:    {revision}")
        print(f"Scope:       {scope}")
        print(f"Destination: {dest}")

    # Auth kwargs (set by your PS script via env var)
    hf_token = os.environ.get("HUGGINGFACE_HUB_TOKEN", "")
    # Build kwargs separately for HfApi.repo_info and snapshot_download
    api = HfApi()
    repo_info_kwargs = _build_auth_kwargs(api.repo_info, hf_token)
    dl_kwargs = _build_auth_kwargs(snapshot_download, hf_token)

    try:
        # Validate repo/revision access (uses auth exactly once)
        api.repo_info(repo_id=repo_id, revision=revision, repo_type=repo_type, **repo_info_kwargs)

        # Download
        snapshot_download(
            repo_id=repo_id,
            revision=revision,
            repo_type=repo_type,
            allow_patterns=allow_patterns,
            local_dir=str(dest),
            local_dir_use_symlinks=local_dir_use_symlinks,
            resume_download=True,
            max_workers=8,
            **dl_kwargs,   # <- token/use_auth_token passed once, matching signature
        )

        if not args.quiet:
            print("✅ Download complete.")

    except HfHubHTTPError as http_err:
        print(f"HTTP error from Hugging Face Hub: {http_err}", file=sys.stderr)
        sys.exit(1)
    except Exception as ex:
        print(f"Unexpected error: {ex}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

