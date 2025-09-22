# Pokemon Red - Unlimited Play
# ============================

param(
    [int]$MaxSteps = 50000,
    [string]$ObservationMode = "vision",
    [int]$TokenLimit = 2000,
    [switch]$AutoStart
)

Write-Host ""
Write-Host "=========================================="
Write-Host "Pokemon Red - Unlimited Play"
Write-Host "=========================================="
Write-Host ""

# Configuration
$GAME_NAME = "pokemon_red"
$MODEL_NAME = "llm-studio-qwen/qwen2.5-vl-7b"
$NUM_RUNS = 1
$HARNESS_MODE = "--harness"

Write-Host "Configuration:"
Write-Host "  Game: $GAME_NAME"
Write-Host "  Model: $MODEL_NAME"
Write-Host "  Max Steps: $MaxSteps (unlimited)"
Write-Host "  Observation: $ObservationMode"
Write-Host "  Token Limit: $TokenLimit"
Write-Host ""

Write-Host "WARNING: This will run for several hours!"
Write-Host "The game will continue until:"
Write-Host "  - Pokemon Red story completion"
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
} catch {
    Write-Host "ERROR: Cannot connect to LLM Studio"
    Write-Host "Please ensure LLM Studio is running on localhost:1234"
    if (-not $AutoStart) {
        Read-Host "Press Enter to exit"
    }
    exit 1
}

# ROM check
if (-not (Test-Path "gamingagent\configs\custom_06_pokemon_red\rom\pokemon.gb")) {
    Write-Host "ERROR: Pokemon Red ROM not found"
    Write-Host "Expected: gamingagent\configs\custom_06_pokemon_red\rom\pokemon.gb"
    if (-not $AutoStart) {
        Read-Host "Press Enter to exit"
    }
    exit 1
}

# Create log directory
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logDir = "logs\pokemon_unlimited_$timestamp"
New-Item -ItemType Directory -Path $logDir -Force | Out-Null

Write-Host ""
Write-Host "=========================================="
Write-Host "Starting Pokemon Red Unlimited Session"
Write-Host "=========================================="
Write-Host ""
Write-Host "Session logging to: $logDir"
Write-Host "Progress: cache\pokemon_red\llm_studio_qwen\"
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
Write-Host "Pokemon Red Session Ended"
Write-Host "=========================================="
Write-Host ""
Write-Host "Session ended at: $(Get-Date)"
Write-Host "Exit code: $exitCode"
Write-Host ""

# Show results
if (Test-Path "cache\pokemon_red\llm_studio_qwen\") {
    $latestDir = Get-ChildItem "cache\pokemon_red\llm_studio_qwen\" -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($latestDir) {
        Write-Host "Latest session: cache\pokemon_red\llm_studio_qwen\$($latestDir.Name)"
        $episodeLog = "cache\pokemon_red\llm_studio_qwen\$($latestDir.Name)\episode_001_log.jsonl"
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