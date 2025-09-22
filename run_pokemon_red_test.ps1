# Pokemon Red - Test Run (5 steps)
# ==================================

param(
    [int]$MaxSteps = 5,
    [string]$ObservationMode = "vision",
    [int]$TokenLimit = 2000
)

Write-Host ""
Write-Host "========================================"
Write-Host "Pokemon Red - Test Run ($MaxSteps steps)"
Write-Host "========================================"
Write-Host ""

# Configuration
$GAME_NAME = "pokemon_red"
$MODEL_NAME = "llm-studio-qwen/qwen2.5-vl-7b"
$NUM_RUNS = 1
$HARNESS_MODE = "--harness"

Write-Host "Configuration:"
Write-Host "  Game: $GAME_NAME"
Write-Host "  Model: $MODEL_NAME"
Write-Host "  Max Steps: $MaxSteps"
Write-Host "  Observation: $ObservationMode"
Write-Host "  Token Limit: $TokenLimit"
Write-Host ""

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
    Read-Host "Press Enter to exit"
    exit 1
}

# Create log directory
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logDir = "logs\pokemon_test_$timestamp"
New-Item -ItemType Directory -Path $logDir -Force | Out-Null

Write-Host ""
Write-Host "Starting test run..."
Write-Host "Log: $logDir\test_output.log"
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
    & python @arguments 2>&1 | Tee-Object -FilePath "$logDir\test_output.log"
    $exitCode = $LASTEXITCODE
} catch {
    Write-Host "Error during execution: $_"
    $exitCode = -1
}

Write-Host ""
Write-Host "Test completed. Exit code: $exitCode"
if ($exitCode -eq 0) {
    Write-Host "SUCCESS: Test run completed successfully!"
} else {
    Write-Host "FAILED: Check $logDir\test_output.log for details"
}

Write-Host ""
Read-Host "Press Enter to exit"