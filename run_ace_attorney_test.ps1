# Ace Attorney - Quick Test with Local LLM
# =========================================

param(
    [int]$MaxSteps = 100,
    [string]$ObservationMode = "both"
)

# Set output encoding to UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ""
Write-Host "=========================================="
Write-Host "Ace Attorney - Quick Test (Local LLM)"
Write-Host "=========================================="
Write-Host ""

# Configuration
$GAME_NAME = "ace_attorney"
$MODEL_NAME = "llm-studio-Qwen/Qwen2.5-VL-32B-Instruct"
$NUM_RUNS = 1
$HARNESS_MODE = "--harness"

Write-Host "Configuration:"
Write-Host "  Game: $GAME_NAME"
Write-Host "  Model: $MODEL_NAME"
Write-Host "  Max Steps: $MaxSteps (test mode)"
Write-Host "  Observation: $ObservationMode"
Write-Host ""

# LLM Studio check
Write-Host "Checking LLM Studio connection..."
try {
    $response = Invoke-RestMethod -Uri "http://localhost:1234/v1/models" -Method Get -TimeoutSec 5
    Write-Host "[OK] LLM Studio: Connected"
} catch {
    Write-Host "[ERROR] Cannot connect to LLM Studio (localhost:1234)"
    Write-Host ""
    Write-Host "Please start LLM Studio and load a multimodal model"
    Read-Host "Press Enter to exit"
    exit 1
}

# ROM check
$romPath = "gamingagent\configs\retro_02_ace_attorney\rom\PhoenixWright_AceAttorney_JusticeforAll.gba"
if (-not (Test-Path $romPath)) {
    Write-Host "[ERROR] ROM not found at $romPath"
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "[OK] ROM: Found"

# Retro environment ROM check
$retroEnvPath = "gamingagent\envs\retro_02_ace_attorney\AceAttorney-GbAdvance\rom.gba"
if (-not (Test-Path $retroEnvPath)) {
    Write-Host "Copying ROM to retro environment..."
    Copy-Item $romPath $retroEnvPath -Force
    Write-Host "[OK] ROM: Copied to environment"
}

# Check stable-retro
Write-Host "Checking stable-retro..."
$retroCheck = python -c "import retro; print('OK')" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] stable-retro not installed"
    Write-Host ""
    Write-Host "To install stable-retro on Windows:"
    Write-Host "  1. Install CMake: https://cmake.org/download/"
    Write-Host "  2. Install Visual Studio Build Tools"
    Write-Host "  3. Run: pip install stable-retro"
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "[OK] stable-retro: Installed"

Write-Host ""
Write-Host "Starting test session..."
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
& python @arguments

Write-Host ""
Write-Host "=========================================="
Write-Host "Test Complete"
Write-Host "=========================================="
Write-Host ""

# Show results
if (Test-Path "cache\retro_ace_attorney\") {
    $latestDir = Get-ChildItem "cache\retro_ace_attorney\" -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($latestDir) {
        Write-Host "Session directory: cache\retro_ace_attorney\$($latestDir.Name)"
        $episodeLog = "cache\retro_ace_attorney\$($latestDir.Name)\episode_001_log.jsonl"
        if (Test-Path $episodeLog) {
            $stepCount = (Get-Content $episodeLog | Measure-Object -Line).Lines
            Write-Host "Steps completed: $stepCount"
        }
    }
}

Write-Host ""
Read-Host "Press Enter to exit"
