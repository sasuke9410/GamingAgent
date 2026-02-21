# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 一般的なコマンド

### 環境セットアップ
```bash
# 依存関係のインストール
pip install -e .

# API キーの設定
source credentials.sh
```

### 評価実行
```bash
# 単一モデル・単一ゲームの評価
python3 lmgame-bench/single_agent_runner.py --game_name sokoban --model_name claude-3-5-sonnet --config_root_dir gamingagent/configs

# 複数ゲームでの評価（並列実行）
python3 lmgame-bench/run.py --model_name claude-3-5-sonnet --game_names sokoban,tetris,candy_crush,twenty_forty_eight --harness_mode both

# 全モデルの評価
bash lmgame-bench/evaluate_all.sh
```

### テスト実行
```bash
# 基本テスト
python tests/test_run.py

# Pokemon Red環境テスト
python tests/pokemon_red_test/test_game_env.py
```

## アーキテクチャ概要

### 主要コンポーネント

1. **GamingAgent Framework** (`gamingagent/`)
   - **Agents** (`agents/`): `BaseAgent`を継承したゲーム固有のエージェント実装
   - **Modules** (`modules/`): モジュラー設計による認知アーキテクチャ
     - `BaseModule`: 直接的な観察→行動変換
     - `PerceptionModule`: 視覚・テキスト観察の処理
     - `MemoryModule`: エピソード記憶管理
     - `ReasoningModule`: 推論と行動決定
   - **Environments** (`envs/`): ゲーム環境のGym/Retroインターフェース実装

2. **LMGame Bench** (`lmgame-bench/`)
   - **評価フレームワーク**: モデル性能のベンチマーク
   - **並列実行エンジン**: 複数のゲーム/モデル組み合わせの効率的評価

3. **Computer Use** (`computer_use/`)
   - **実時間ゲーミング**: PC/ラップトップでの実時間エージェント実行

### 設定システム

- **ゲーム設定**: `gamingagent/configs/{game_name}/config.yaml`
  - 環境パラメータ（max_steps、num_runs等）
  - エージェント設定（model_name、harness、observation_mode等）
  - モジュール固有設定（memory容量、推論設定等）

- **プロンプト管理**: `gamingagent/configs/{game_name}/module_prompts.json`

### サポートされるゲーム

**Gymnasium環境**:
- 2048 (`custom_01_2048`)
- Sokoban (`custom_02_sokoban`)
- Candy Crush (`custom_03_candy_crush`)
- Tetris (`custom_04_tetris`)
- Pokemon Red (`custom_06_pokemon_red`) - ROM必須
- Doom (`custom_05_doom`)

**Retro環境**:
- Super Mario Bros (`retro_01_super_mario_bros`)
- Ace Attorney (`retro_02_ace_attorney`)

**マルチエージェント**:
- Tic Tac Toe (`zoo_01_tictactoe`)
- Texas Hold'em (`zoo_02_texasholdem`)

### モデルサポート

**クラウドモデル**:
OpenAI (o4-mini, o3, gpt-4o)、Anthropic (Claude-4, Claude-3.5)、Gemini (2.5-pro, 2.0-flash)、xAI (grok-3-mini)、Deepseek (reasoner, chat)に対応。API設定は`credentials.sh`で管理。

**ローカルモデル**:
- **LLM Studio**: `llm-studio-{model_name}`形式でサポート（例: `llm-studio-Qwen/Qwen2.5-VL-32B-Instruct`）
- **vLLM**: `vllm-{model_name}`形式でサポート
- **Modal**: `modal-{model_name}`形式でサポート

### マルチモーダル要件

**マルチモーダルモデルが必要な場合**:
- `observation_mode: "vision"` - 画像のみの観察
- `observation_mode: "vision_text"` - 画像＋テキストの観察
- ゲーム画面キャプチャを処理する必要がある場合

**テキストのみモデルで十分な場合**:
- `observation_mode: "text"` - テキストのみの観察
- ゲーム状態がテキストで完全に表現できる場合（Sokoban、2048、Tetris等）

### LLM Studioローカルモデル設定

```python
# APIManagerでLLM Studio設定
api_manager = APIManager(
    game_name="sokoban",
    llm_studio_host="localhost",  # LLM Studioサーバーホスト
    llm_studio_port=1234,         # LLM Studioサーバーポート
    llm_studio_api_key="not-needed"  # APIキー（通常不要）
)

# モデル名の指定
model_name = "llm-studio-Qwen/Qwen2.5-VL-32B-Instruct"  # マルチモーダル対応
# または
model_name = "llm-studio-Qwen/Qwen2.5-32B-Instruct"     # テキストのみ
```

### 重要な設計パターン

- **Harness Mode**: `harness=true`で認知モジュールパイプライン使用、`false`で直接的な基本モジュール使用
- **Observation Mode**: `"vision"`（画像ベース）または`"text"`（テキストベース）
- **キャッシュシステム**: `cache_dir`での実行結果とモデル応答の保存
- **並列評価**: ProcessPoolExecutorによる効率的なベンチマーク実行

### 新しいゲームの追加

1. `gamingagent/envs/`に環境実装を追加
2. `gamingagent/configs/`に設定ファイルを作成
3. 必要に応じてROMファイルを指定ディレクトリに配置（Pokemon Red、Ace Attorney等）

### ROHファイル要件

- **Pokemon Red**: `gamingagent/configs/custom_06_pokemon_red/rom/pokemon.gb`
- **Ace Attorney**: `gamingagent/envs/retro_02_ace_attorney/AceAttorney-GbAdvance/`

### LLM Studioローカルモデル使用例

```bash
# LLM Studioサーバーを起動（ポート1234）
# マルチモーダルモデルで評価
python3 lmgame-bench/single_agent_runner.py \
  --game_name sokoban \
  --model_name llm-studio-Qwen/Qwen2.5-VL-32B-Instruct \
  --config_root_dir gamingagent/configs \
  --harness

# テキストのみモデルで評価
python3 lmgame-bench/single_agent_runner.py \
  --game_name twenty_forty_eight \
  --model_name llm-studio-Qwen/Qwen2.5-32B-Instruct \
  --config_root_dir gamingagent/configs
```

### ローカルモデル設定のデバッグ

```bash
# LLM Studioサーバーが正常に動作しているか確認
curl http://localhost:1234/v1/models

# APIManagerでの接続テスト
python3 -c "
from tools.serving import APIManager
api = APIManager('test', llm_studio_host='localhost', llm_studio_port=1234)
result, costs = api.text_only_completion(
    'llm-studio-your-model-name',
    'You are a helpful assistant.',
    'Hello, how are you?'
)
print(result)
"
```

### 注意事項

- LLM Studio使用時は事前にサーバーが起動していることを確認
- マルチモーダルゲーム（Pokemon Red、Super Mario Bros等）では必ずマルチモーダル対応モデルを使用
- テキストのみゲーム（2048、Sokoban、Tetris等）では軽量なテキストモデルの使用を推奨
- ローカルモデルの推論速度がクラウドAPIより遅い場合があるため、`token_limit`を適切に調整