# Ace Attorney - Unlimited Play with Local LLM
# ============================================

param(
    [int]$MaxSteps = 50000,
    [string]$ObservationMode = "both",
    [int]$TokenLimit = 1500,
    [switch]$AutoStart
)

# Set output encoding to UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ""
Write-Host "=========================================="
Write-Host "Ace Attorney - Unlimited Play (Local LLM)"
Write-Host "=========================================="
Write-Host ""

# Configuration
$GAME_NAME = "ace_attorney"
$MODEL_NAME = "llm-studio-Qwen/Qwen2.5-VL-32B-Instruct"  # マルチモーダル対応モデル
$NUM_RUNS = 1
$HARNESS_MODE = "--harness"

Write-Host "Configuration:"
Write-Host "  Game: $GAME_NAME"
Write-Host "  Model: $MODEL_NAME"
Write-Host "  Max Steps: $MaxSteps"
Write-Host "  Observation: $ObservationMode"
Write-Host "  Token Limit: $TokenLimit"
Write-Host ""

Write-Host "WARNING: This will run for several hours!"
Write-Host "The game will continue until:"
Write-Host "  - Ace Attorney case completion"
Write-Host "  - Manual interruption (Ctrl+C)"
Write-Host "  - Context length exceeded"
Write-Host ""

if (-not $AutoStart) {
    $confirm = Read-Host "Continue with unlimited gameplay? (y/N)"
    if ($confirm -ne "y" -and $confirm -ne "Y") {
        Write-Host "Cancelled."
        exit
    }
}

# Environment setup
if (-not $env:VIRTUAL_ENV) {
    if (Test-Path ".venv\Scripts\Activate.ps1") {
        & .venv\Scripts\Activate.ps1
        Write-Host "Virtual environment activated"
    }
}

# LLM Studio check
Write-Host "Checking LLM Studio connection..."
try {
    $response = Invoke-RestMethod -Uri "http://localhost:1234/v1/models" -Method Get -TimeoutSec 5
    Write-Host "LLM Studio: Connected"
    Write-Host "Available model: $($response.data[0].id)"
} catch {
    Write-Host "ERROR: Cannot connect to LLM Studio"
    Write-Host "Please ensure LLM Studio is running on localhost:1234"
    Write-Host "Load a multimodal model (e.g., Qwen2.5-VL-32B-Instruct)"
    if (-not $AutoStart) {
        Read-Host "Press Enter to exit"
    }
    exit 1
}

# ROM check
$romPath = "gamingagent\configs\retro_02_ace_attorney\rom\PhoenixWright_AceAttorney_JusticeforAll.gba"
if (-not (Test-Path $romPath)) {
    Write-Host "ERROR: Ace Attorney ROM not found"
    Write-Host "Expected: $romPath"
    if (-not $AutoStart) {
        Read-Host "Press Enter to exit"
    }
    exit 1
}

# Retro environment check
$retroEnvPath = "gamingagent\envs\retro_02_ace_attorney\AceAttorney-GbAdvance\rom.gba"
if (-not (Test-Path $retroEnvPath)) {
    Write-Host "Copying ROM to retro environment..."
    Copy-Item $romPath $retroEnvPath -Force
    Write-Host "ROM copied successfully"
}

# Check stable-retro installation
Write-Host ""
Write-Host "Checking stable-retro installation..."
$retroCheck = python -c "import retro; print('OK')" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: stable-retro is not installed"
    Write-Host ""
    Write-Host "Please install stable-retro manually:"
    Write-Host "  1. Install CMake: https://cmake.org/download/"
    Write-Host "  2. Install Visual Studio Build Tools"
    Write-Host "  3. Run: pip install stable-retro"
    Write-Host ""
    if (-not $AutoStart) {
        Read-Host "Press Enter to exit"
    }
    exit 1
}
Write-Host "stable-retro: Installed"

# Create log directory
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logDir = "logs\ace_attorney_unlimited_$timestamp"
New-Item -ItemType Directory -Path $logDir -Force | Out-Null

Write-Host ""
Write-Host "=========================================="
Write-Host "Starting Ace Attorney Unlimited Session"
Write-Host "=========================================="
Write-Host ""
Write-Host "Session logging to: $logDir"
Write-Host "Progress: cache\retro_ace_attorney\"
Write-Host ""
Write-Host "CONTROLS:"
Write-Host "  Ctrl+C: Stop safely"
Write-Host ""

# Build arguments
$arguments = @(
    "-c"
    "import sys; sys.path.insert(0, '.'); exec(open('lmgame-bench/single_agent_runner.py').read())"
    "--game_name"
    $GAME_NAME
    "--model_name"
    $MODEL_NAME
    "--config_root_dir"
    "gamingagent/configs"
    $HARNESS_MODE
    "--num_runs"
    $NUM_RUNS
    "--max_steps_per_episode"
    $MaxSteps
    "--observation_mode"
    $ObservationMode
)

# Execute
try {
    & python @arguments 2>&1 | Tee-Object -FilePath "$logDir\session_output.log"
    $exitCode = $LASTEXITCODE
} catch {
    Write-Host "Error during execution: $_"
    $exitCode = -1
}

Write-Host ""
Write-Host "=========================================="
Write-Host "Ace Attorney Session Ended"
Write-Host "=========================================="
Write-Host ""
Write-Host "Session ended at: $(Get-Date)"
Write-Host "Exit code: $exitCode"
Write-Host ""

# Show results
if (Test-Path "cache\retro_ace_attorney\") {
    $latestDir = Get-ChildItem "cache\retro_ace_attorney\" -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($latestDir) {
        Write-Host "Latest session: cache\retro_ace_attorney\$($latestDir.Name)"
        $episodeLog = "cache\retro_ace_attorney\$($latestDir.Name)\episode_001_log.jsonl"
        if (Test-Path $episodeLog) {
            $stepCount = (Get-Content $episodeLog | Measure-Object -Line).Lines
            Write-Host "Total steps completed: $stepCount"
        }
    }
}

Write-Host ""
Write-Host "Results saved to: $logDir\session_output.log"
if (-not $AutoStart) {
    Read-Host "Press Enter to exit"
}
