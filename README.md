# huggingface_downloader

Mirror files from a Hugging Face repo (optionally just a subfolder) **directly from its webpage URL** into a local directory. Works with models, datasets, and spaces. Supports private/gated repos via token, preserves directory structure, and resumes cleanly.

## Features
- 🔗 **URL-based**: paste any HF repo URL (branch + optional subfolder)
- 🗂️ **Subfolder-only** downloads using `allow_patterns`
- 🔒 **Private/gated** access via `HUGGINGFACE_HUB_TOKEN` (or `huggingface-cli login`)
- ♻️ **Resumable** downloads (`resume_download=True`)
- 🧭 **Version-agnostic auth** (handles both `token` and legacy `use_auth_token`)
- 🪟 **Optional PowerShell launcher** for Windows

---

## Supported URL forms
- `https://huggingface.co/<owner>/<repo>`
- `https://huggingface.co/<owner>/<repo>/tree/<branch>`
- `https://huggingface.co/<owner>/<repo>/tree/<branch>/<path/inside>`
- Datasets: `https://huggingface.co/datasets/<owner>/<repo>`
- Spaces:   `https://huggingface.co/spaces/<owner>/<repo>`

---

## Quick start

```bash
git clone https://github.com/<your-username>/huggingface_downloader.git
cd huggingface_downloader
python -m venv venv
# Windows: .\venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -U huggingface_hub packaging
```

---

## Usage (Python)

**Entire repo (defaults to `main` if `/tree` not provided):**
```bash
python hf_grab.py "https://huggingface.co/acme/awesome-model" ./out
```

**Specific branch root:**
```bash
python hf_grab.py "https://huggingface.co/acme/awesome-model/tree/dev" ./out
```

**Subfolder only:**
```bash
python hf_grab.py "https://huggingface.co/acme/awesome-model/tree/main/models/onnx" ./onnx_only
```

**Quiet mode:**
```bash
python hf_grab.py "https://huggingface.co/acme/awesome-model/tree/main" ./out --quiet
```

---

## Authentication (private/gated repos)

1) Create a **Read** token on Hugging Face (Settings → Access Tokens).  
2) If the repo is gated, click **“Agree and access”** on its page while logged in.  
3) Provide the token:

**Option A: environment variable**
```bash
# macOS/Linux
export HUGGINGFACE_HUB_TOKEN=hf_xxx

# Windows (PowerShell, current session)
$env:HUGGINGFACE_HUB_TOKEN="hf_xxx"
```

**Option B: login once**
```bash
huggingface-cli login
```

The script detects your installed `huggingface_hub` version and uses the correct parameter (`token` or legacy `use_auth_token`) automatically.

---

## Windows PowerShell launcher (optional)

`hf_download.ps1` wraps the Python script, sets the token **for this run only**, and gives clearer logs.

**Examples:**
```powershell
# First time (if Windows blocked the script):
Unblock-File .\hf_download.ps1

# Use your virtualenv Python and prompt for token securely
.\hf_download.ps1 \
  -Url "https://huggingface.co/acme/awesome-model/tree/main" \
  -Dest ".\out" \
  -PythonExe ".\venv\Scripts\python.exe" \
  -ScriptPath ".\hf_grab.py" \
  -ForceTokenPrompt

# Or pass the token directly
.\hf_download.ps1 \
  -Url "https://huggingface.co/acme/awesome-model/tree/main" \
  -Dest ".\out" \
  -Token "hf_xxx" \
  -PythonExe ".\venv\Scripts\python.exe" \
  -ScriptPath ".\hf_grab.py"
```

## Powershell Example 
### Change specifics for your use case.
- **Steps**:
- **1**: Navigate to your folder where the script is located. In the explorer folder window, click the address then type: "powershell"
- **2**: Activate your venv.Assuming it's called "venv" and it is where you installed your requirements activate it like this:
  ```bash
  venv\scripts\activate
  ```
- **3**: Copy the below script, changing the specific examples to whatever you wish. Below is a private key required repository and it will prompt you for your private key. After entering, it will download this repo in its entirety.  
```bash
.\hf_download.ps1 `
  -Url "https://huggingface.co/briaai/FIBO/tree/main" `
  -Dest ".\imagecore\models\huggingface\briaai" `
  -PythonExe ".\venv\Scripts\python.exe" `
  -ScriptPath ".\hf_grab.py" `
  -ForceTokenPrompt
```

---

## Tips & customization

- **Skip large weights** (edit `hf_grab.py` and add to the `snapshot_download(...)` call):
  ```python
  ignore_patterns=["*.safetensors","*.bin","*.pt","*.ckpt"]
  ```
- **Keep structure**: downloads mirror the repo’s directory layout under your destination.
- **Resume**: re-running only fetches missing/corrupted files.
- **Datasets/Spaces**: URLs with `/datasets/` or `/spaces/` are auto-detected.

---

## Requirements

- Python **3.8+**
- [`huggingface_hub`](https://pypi.org/project/huggingface-hub/)
- [`packaging`](https://pypi.org/project/packaging/)

Install:
```bash
pip install -U huggingface_hub packaging
```

---

## Troubleshooting

- **Only README/empty folders download**  
  Token missing/invalid, or you haven’t accepted the repo’s terms.
- **403/404**  
  Your account/token lacks access; confirm permissions and URL.
- **“multiple values for keyword argument 'token'”**  
  You’re importing private internals or passing auth twice. This repo’s `hf_grab.py` uses the public import and passes auth exactly once based on the installed function signature.
- **Windows PS errors**  
  Run from a PowerShell window (not right-click). If blocked: `Unblock-File .\hf_download.ps1`.

---

## License

For personal / non-commercial use. 
- **Code**: Prosperity Public License 3.0.0 (non-commercial; contact for commercial use)  
 
---

## Contributing

Issues and PRs welcome!  
If you’d like CLI flags for include/exclude globs or other enhancements, open a ticket with your use case.

---

## Acknowledgements

Built on top of the excellent [`huggingface_hub`](https://github.com/huggingface/huggingface_hub) library.
