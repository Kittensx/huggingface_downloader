
param(
  [Parameter(Mandatory = $true)] [string]$Url,
  [Parameter(Mandatory = $true)] [string]$Dest,
  [string]$Token,
  [string]$PythonExe,
  [string]$ScriptPath,
  [switch]$Quiet,
  [switch]$ForceTokenPrompt
)

$ErrorActionPreference = 'Stop'
if (-not $PSBoundParameters.ContainsKey('PythonExe'))  { $PythonExe  = 'python' }
if (-not $PSBoundParameters.ContainsKey('ScriptPath')) { $ScriptPath = '.\hf_grab.py' }

function Resolve-OrCreate-Dest { param([string]$Path)
  if (-not (Test-Path -LiteralPath $Path)) { New-Item -ItemType Directory -Path $Path -Force | Out-Null }
  (Resolve-Path -LiteralPath $Path).Path
}
function Read-Token-Secure {
  $sec = Read-Host "Enter HUGGINGFACE_HUB_TOKEN (input hidden)" -AsSecureString
  if (-not $sec) { return $null }
  (New-Object System.Net.NetworkCredential("", $sec)).Password
}

if (-not (Test-Path -LiteralPath $ScriptPath)) { throw "Cannot find hf_grab.py at: $ScriptPath" }
try { $null = & $PythonExe -V } catch { throw "Could not run Python at '$PythonExe'." }

$destPath = Resolve-OrCreate-Dest -Path $Dest
if ($ForceTokenPrompt -or [string]::IsNullOrWhiteSpace($Token)) { $Token = Read-Token-Secure }

if (-not [string]::IsNullOrWhiteSpace($Token)) {
  # Use either of the next two lines (both are OK). Keep ONLY one.
  # $env:HUGGINGFACE_HUB_TOKEN = $Token
  [System.Environment]::SetEnvironmentVariable('HUGGINGFACE_HUB_TOKEN', $Token, 'Process')
  Write-Host "Token set for this process."
} else {
  Write-Host "No token provided. Private/gated files may NOT download."
}

$argsList = @("$ScriptPath", "$Url", "$destPath")
if ($Quiet) { $argsList += "--quiet" }

Write-Host "Running:" ($PythonExe + " " + ($argsList -join " "))
& $PythonExe @argsList
if ($LASTEXITCODE -ne 0) { throw "hf_grab.py exited with code $LASTEXITCODE" }
Write-Host "Download complete → $destPath"



