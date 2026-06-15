$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = Join-Path $Root ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $Python)) {
    python -m venv (Join-Path $Root ".venv")
}

& $Python -m pip install -r (Join-Path $Root "requirements.txt")
& $Python (Join-Path $Root "app.py")
