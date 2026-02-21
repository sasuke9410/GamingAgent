# Pokemon Red - Quick Test
# =========================

param(
    [int]$MaxSteps = 50,
    [string]$ObservationMode = "vision"
)

# Set output encoding to UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ""
Write-Host "=========================================="
Write-Host "Pokemon Red - Quick Test"
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
Write-Host "  Max Steps: $MaxSteps (test mode)"
Write-Host "  Observation: $ObservationMode"
Write-Host ""

# LLM Studio check
Write-Host "Checking LLM Studio connection..."
try {
    $response = Invoke-RestMethod -Uri "http://localhost:1234/v1/models" -Method Get -TimeoutSec 5
    Write-Host "[OK] LLM Studio: Connected"
    Write-Host "[OK] Model loaded: $($response.data[0].id)"
} catch {
    Write-Host "[ERROR] Cannot connect to LLM Studio (localhost:1234)"
    Write-Host ""
    Write-Host "Please start LLM Studio and load qwen2.5-vl-7b model"
    Read-Host "Press Enter to exit"
    exit 1
}

# ROM check
$romPath = "gamingagent\configs\custom_06_pokemon_red\rom\pokemon.gb"
if (-not (Test-Path $romPath)) {
    Write-Host "[ERROR] Pokemon Red ROM not found"
    Write-Host "Expected: $romPath"
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "[OK] ROM: Found"

# Check PyBoy
Write-Host ""
Write-Host "Checking PyBoy installation..."
$pyboyCheck = python -c "import pyboy; print('OK')" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] PyBoy not installed"
    Write-Host "Run: pip install pyboy"
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "[OK] PyBoy: Installed"

# Check Japanese text mapping
Write-Host ""
Write-Host "Checking Japanese text mapping..."
$japaneseMapPath = "gamingagent\configs\custom_06_pokemon_red\character_map.json"
if (Test-Path $japaneseMapPath) {
    Write-Host "[OK] Japanese character map: Found"
    $mapContent = Get-Content $japaneseMapPath -Raw | ConvertFrom-Json
    $charCount = ($mapContent.PSObject.Properties | Measure-Object).Count
    Write-Host "[OK] Character mappings: $charCount entries"
} else {
    Write-Host "[WARNING] Japanese character map not found at: $japaneseMapPath"
}

# Create log directory
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logDir = "logs\pokemon_test_$timestamp"
New-Item -ItemType Directory -Path $logDir -Force | Out-Null

Write-Host ""
Write-Host "Starting test session..."
Write-Host "Logs will be saved to: $logDir"
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
& python @arguments 2>&1 | Tee-Object -FilePath "$logDir\test_output.log"

Write-Host ""
Write-Host "=========================================="
Write-Host "Test Complete"
Write-Host "=========================================="
Write-Host ""

# Analyze results
if (Test-Path "cache\pokemon_red\llm_studio_qwen\") {
    $latestDir = Get-ChildItem "cache\pokemon_red\llm_studio_qwen\" -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($latestDir) {
        Write-Host "Latest session: cache\pokemon_red\llm_studio_qwen\$($latestDir.Name)"

        # Check episode log
        $episodeLog = "cache\pokemon_red\llm_studio_qwen\$($latestDir.Name)\episode_001_log.jsonl"
        if (Test-Path $episodeLog) {
            $stepCount = (Get-Content $episodeLog | Measure-Object -Line).Lines
            Write-Host "Steps completed: $stepCount"

            # Check for Japanese text in logs
            Write-Host ""
            Write-Host "Checking for Japanese text in observations..."
            $logContent = Get-Content $episodeLog -Raw
            if ($logContent -match '[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]') {
                Write-Host "[OK] Japanese characters detected in logs"
            } else {
                Write-Host "[INFO] No Japanese characters found (may be normal for early game)"
            }

            # Show last observation
            Write-Host ""
            Write-Host "Last observation from log:"
            $lastLine = Get-Content $episodeLog -Tail 1 | ConvertFrom-Json
            if ($lastLine.agent_observation.text_representation) {
                Write-Host "---"
                Write-Host $lastLine.agent_observation.text_representation
                Write-Host "---"
            }
        }

        # Check memory module
        $memoryLog = "cache\pokemon_red\llm_studio_qwen\$($latestDir.Name)\memory_log.jsonl"
        if (Test-Path $memoryLog) {
            $memoryCount = (Get-Content $memoryLog | Measure-Object -Line).Lines
            Write-Host ""
            Write-Host "[OK] Memory log found: $memoryCount entries"

            # Show last memory entry
            $lastMemory = Get-Content $memoryLog -Tail 1 | ConvertFrom-Json
            Write-Host "Last memory entry:"
            Write-Host "  Step: $($lastMemory.step)"
            Write-Host "  Action: $($lastMemory.action)"
        } else {
            Write-Host ""
            Write-Host "[WARNING] Memory log not found"
        }
    }
}

Write-Host ""
Write-Host "Full logs saved to: $logDir\test_output.log"
Write-Host ""
Read-Host "Press Enter to exit"
