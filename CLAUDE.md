# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 環境セットアップと起動手順

### Windows（uv） — Gymnasium系ゲーム用

| 対応ゲーム | 非対応 |
|-----------|--------|
| Pokemon Red / 2048 / Sokoban / Tetris / Candy Crush / Doom / TicTacToe / TexasHoldem | Ace Attorney / Super Mario Bros（stable-retro 非対応） |

```bash
# 初回セットアップ（.venv は既存）
uv sync

# 起動
.venv\Scripts\activate          # Windows PowerShell/CMD
source .venv/Scripts/activate   # Git Bash / この環境

source credentials.sh           # APIキー設定

# 例: Pokemon Red
python lmgame-bench/single_agent_runner.py \
  --game_name pokemon_red \
  --model_name gemini-2.0-flash \
  --config_root_dir gamingagent/configs \
  --harness
```

### WSL2（~/lmgame-venv） — Retro系ゲームを含む全ゲーム用

| 対応ゲーム |
|-----------|
| 全ゲーム（Ace Attorney / Super Mario Bros を含む） |

```bash
# 初回セットアップ（初回のみ）
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# シンボリックリンク（Windowsとソース共有）
ln -sfn /mnt/c/Users/sasuke/Documents/GamingAgent ~/GamingAgent

# venv作成（system-site-packages でstable-retroを取り込む）
uv venv ~/lmgame-venv --python 3.12 --system-site-packages
UV_LINK_MODE=copy uv pip install --python ~/lmgame-venv/bin/python \
    anthropic==0.49.0 openai google-generativeai==0.8.4 google-genai==1.5.0 \
    numpy pyyaml "gymnasium>=0.29" pyboy pillow tiktoken together \
    psutil pettingzoo opencv-python-headless aiohttp pyglet
UV_LINK_MODE=copy uv pip install --python ~/lmgame-venv/bin/python \
    -e /mnt/c/Users/sasuke/Documents/GamingAgent --no-deps

# 起動（毎回）
source ~/lmgame-venv/bin/activate
cd ~/GamingAgent
source /mnt/c/Users/sasuke/Documents/GamingAgent/credentials.sh

# 例: Ace Attorney
python lmgame-bench/single_agent_runner.py \
  --game_name ace_attorney \
  --model_name gemini-2.5-flash-preview-04-17 \
  --config_root_dir gamingagent/configs \
  --harness

# 例: Super Mario Bros
python lmgame-bench/single_agent_runner.py \
  --game_name super_mario_bros \
  --model_name gemini-2.0-flash \
  --config_root_dir gamingagent/configs
```

> **WSL2 ディスプレイ**: Windows 11 の WSLg が自動的に `DISPLAY=:0` を設定するため通常は追加設定不要。

### 評価実行
```bash
# 単一ゲーム・単一モデル
python3 lmgame-bench/single_agent_runner.py --game_name sokoban --model_name claude-3-5-sonnet --config_root_dir gamingagent/configs

# ハーネスあり（認知モジュールパイプライン使用）
python3 lmgame-bench/single_agent_runner.py --game_name sokoban --model_name claude-3-5-sonnet --config_root_dir gamingagent/configs --harness

# 複数ゲーム並列評価
python3 lmgame-bench/run.py --model_name claude-3-5-sonnet --game_names sokoban,tetris,candy_crush,twenty_forty_eight --harness_mode both

# 全モデル評価
bash lmgame-bench/evaluate_all.sh
```

### テスト
```bash
python tests/test_run.py
python tests/pokemon_red_test/test_game_env.py
```

### ゲームリプレイ動画生成
```bash
python eval/video_generation_script.py --agent_config_path [CONFIG_PATH] --episode_log_path [LOG_PATH] --method text --output_path [OUTPUT_NAME] --fps 2
```

### LLM Studio接続確認
```bash
curl http://localhost:1234/v1/models
```

## アーキテクチャ

### 2つの実行モード

**Harness Mode** (`--harness`): Perception → Memory → Reasoning の3段階認知パイプライン。過去のゲーム状態を記憶し、反省・推論を行う高度なエージェント動作。

**Base Mode** (デフォルト): 観察を直接行動に変換する単純モード。ベンチマーク評価に適している。

### モジュール構成 (`gamingagent/modules/`)

| モジュール | ファイル | 役割 |
|----------|--------|-----|
| CoreModule | `core_module.py` | LLM推論インターフェース基底クラス、`GameTrajectory`・`Observation`データクラス定義 |
| BaseModule | `base_module.py` | 観察→行動の直接変換（Base Mode用） |
| PerceptionModule | `perception_module.py` | 視覚・テキスト観察の処理とゲーム状態抽出 |
| MemoryModule | `memory_module.py` | エピソード記憶管理・反省生成 |
| ReasoningModule | `reasoning_module.py` | 戦略的意思決定・行動計画 |

### 設定システム

各ゲームは `gamingagent/configs/{game_name}/` に2ファイルを持つ：
- **`config.yaml`**: 環境パラメータ（max_steps, num_runs）、エージェント設定（model_name, observation_mode, harness）
- **`module_prompts.json`**: 各認知モジュール用のsystem/userプロンプトテンプレート

### 観察モード

- `observation_mode: "vision"` → 画像のみ（マルチモーダルモデル必須）
- `observation_mode: "text"` → テキストのみ（Sokoban、2048、Tetris等）
- `observation_mode: "vision_text"` → 画像＋テキスト（マルチモーダルモデル必須）

### サポートゲーム

**Gymnasium環境** (`gamingagent/envs/custom_*/`):
- `custom_01_2048`, `custom_02_sokoban`, `custom_03_candy_crush`, `custom_04_tetris`
- `custom_05_doom`, `custom_06_pokemon_red`（ROMファイル必須）

**Retro環境** (`gamingagent/envs/retro_*/`):
- `retro_01_super_mario_bros`（stable-retroのインポート必要）
- `retro_02_ace_attorney`（ROMを`envs/retro_02_ace_attorney/AceAttorney-GbAdvance/`に配置）

**マルチエージェント** (`gamingagent/envs/zoo_*/`):
- `zoo_01_tictactoe`, `zoo_02_texasholdem`

### APIとモデルサポート (`tools/serving/`)

`api_manager.py` が全APIプロバイダーを統一管理。コスト計算・トークンカウント・ログ記録も担当。

**クラウドモデル**: OpenAI (o4-mini, o3, gpt-4o)、Anthropic (claude-4系, claude-3-5系)、Gemini (2.5-pro, 2.0-flash)、xAI (grok-3-mini)、Deepseek (R1, V3)

**ローカルモデル**:
- LLM Studio: `llm-studio-{model_name}`（例: `llm-studio-Qwen/Qwen2.5-VL-32B-Instruct`）
- vLLM: `vllm-{model_name}`
- Modal: `modal-{model_name}`

APIキーは`credentials.sh`で管理（`source credentials.sh`で読み込み）。

### キャッシュとログ

実行結果は `cache/{game_name}/{model_name}/{timestamp}/` に保存（JSONL形式のエピソードログ、画像、APIレスポンス）。評価ログは `logs/` に出力。

## ROMファイル要件

- **Pokemon Red**: `gamingagent/configs/custom_06_pokemon_red/rom/pokemon.gb`
- **Ace Attorney**: `gamingagent/envs/retro_02_ace_attorney/AceAttorney-GbAdvance/`

## 新ゲームの追加手順

1. `gamingagent/envs/` に環境クラスを実装（Gymnasium準拠インターフェース）
2. `gamingagent/configs/{new_game}/config.yaml` と `module_prompts.json` を作成
3. `lmgame-bench/single_agent_runner.py` のゲーム名マッピングに追加

## 改善管理

進行中の課題・改善項目は **`IMPROVEMENTS.md`** で管理。
- Pokemon Red: エージェント思考言語の統一化（優先度：高）
- Pokemon Red: UI操作理解の強化（優先度：高）
- Ace Attorney: stable-retroインストール自動化（優先度：高）
