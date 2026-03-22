# Pokemon Red LLM Studio 実行ガイド

## 必要最小限のファイル構成

### 🎮 実行用ファイル（3つのみ）

1. **`pokemon_red_start.bat`** - 簡単な開始用（テスト5ステップ）
2. **`run_pokemon_red_test.ps1`** - テスト実行用（カスタマイズ可能）
3. **`run_pokemon_unlimited.ps1`** - 無制限プレイ用（50,000ステップ）

## 🚀 クイックスタート

### 1. 基本テスト実行
```batch
# ダブルクリックで実行
pokemon_red_start.bat
```

### 2. カスタマイズテスト
```powershell
# PowerShell で実行
.\run_pokemon_red_test.ps1 -MaxSteps 10 -ObservationMode "vision" -TokenLimit 2000
```

### 3. 無制限プレイ
```powershell
# 50,000ステップの長時間プレイ
.\run_pokemon_unlimited.ps1 -AutoStart
```

## ⚙️ 設定パラメータ

### LLM Studio 設定
- **モデル**: `qwen/qwen2.5-vl-7b`
- **コンテキスト長**: 4096トークン（標準）/ 8192トークン（推奨）
- **ホスト**: `localhost:1234`

### ゲーム設定
- **観察モード**: `vision`（安定）/ `both`（豊富な情報）
- **トークン制限**: `2000`（安定）/ `3000-6000`（コンテキスト長による）
- **最大ステップ**: `5`（テスト）/ `50000`（無制限）

## 📁 必要なファイル

### ROM配置
```
gamingagent/configs/custom_06_pokemon_red/rom/pokemon.gb
```

### 設定ファイル
- `gamingagent/configs/custom_06_pokemon_red/config.yaml`
- `gamingagent/configs/custom_06_pokemon_red/module_prompts.json`

## 🐛 トラブルシューティング

### コンテキスト長エラー
```
Error: context length of only 4096 tokens
```
**解決方法**:
1. LLM Studioでコンテキスト長を8192に拡張
2. `-TokenLimit 2000` を使用
3. `-ObservationMode "vision"` を使用

### LLM Studio接続エラー
```
Cannot connect to LLM Studio
```
**解決方法**:
1. LLM Studioが`localhost:1234`で起動していることを確認
2. モデルが正常にロードされていることを確認

### ROM不見エラー
```
Pokemon Red ROM not found
```
**解決方法**:
1. ROMファイルを正しいパスに配置
2. ファイル名が`pokemon.gb`であることを確認

## 📊 実行結果の確認

### ログ場所
- **テストログ**: `logs/pokemon_test_YYYYMMDD_HHMMSS/`
- **無制限ログ**: `logs/pokemon_unlimited_YYYYMMDD_HHMMSS/`
- **ゲームデータ**: `cache/pokemon_red/llm_studio_qwen/`

### 進行状況確認
```powershell
# 最新セッションのステップ数確認
$latest = Get-ChildItem "cache/pokemon_red/llm_studio_qwen/" -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1
$episodeLog = "cache/pokemon_red/llm_studio_qwen/$($latest.Name)/episode_001_log.jsonl"
$stepCount = (Get-Content $episodeLog | Measure-Object -Line).Lines
Write-Host "Total steps completed: $stepCount"
```

## 🎯 推奨設定

### 安定性重視
```powershell
.\run_pokemon_red_test.ps1 -MaxSteps 10 -ObservationMode "vision" -TokenLimit 2000
```

### 情報豊富（コンテキスト長拡張必要）
```powershell
.\run_pokemon_red_test.ps1 -MaxSteps 10 -ObservationMode "both" -TokenLimit 6000
```

### 長時間プレイ
```powershell
.\run_pokemon_unlimited.ps1 -MaxSteps 50000 -ObservationMode "vision" -TokenLimit 2000
```