<p align="center">
<img src="assets/img/logo.png" alt="lmgame-bench" width="100%" align="center">
</p>

<div align="center"> <h1>LMGame Bench と Gaming Agent</h1> </div>
<p align="center">
  <a href="https://arxiv.org/pdf/2505.15146"><b>📜 論文</b></a> |
  <a href="https://huggingface.co/spaces/lmgame/game_arena_bench"><b>🏆 リーダーボード</b></a> |
  <a href="https://www.youtube.com/channel/UCmuHTmXPhmqYlzNySc6woFw"><b>📺 ギャラリー</b></a> |
  <a href="https://lmgame.org/#/gaming_agent"><b>🌐 ウェブサイト</b></a>
</p>

## はじめに

このリポジトリは、標準化されたインタラクティブなゲーム環境においてLLM/VLMベースのエージェントを評価・展開するフレームワークです。主な機能は以下の2つです：

1. バニラ単一モデルVLM設定（ゲームハーネスなし）で最新モデルを多様なビデオゲームのスイートで評価
2. カスタマイズされたGamingAgentワークフロー（ゲームハーネスあり）でモデルを展開・評価し、ゲームプレイ性能を向上

また、PC・ラップトップ上でリアルタイムにゲームを実行するComputer Use Agent（CUA）の簡易展開ソリューションも提供しています。

<p align="center">
  <img src="assets/img/workflow.png" width="90%">
</p>

## 目次

- [ニュース](#ニュース)
- [インストール](#インストール)
- [APIとモデル](#apiとモデル)
- [LMGame Bench](#lmgame-bench)
  - [セットアップ](#セットアップ)
  - [単一モデル評価](#単一モデル評価)
  - [エージェント評価](#エージェント評価)
  - [ゲームパフォーマンスの分析](#ゲームパフォーマンスの分析)
- [Computer-Use Gaming Agents](#computer-use-gaming-agents)
- [独自ゲームの追加](#独自ゲームの追加)
- [引用](#引用)

## ニュース 🔥

- **[2025/6]** LMGame Benchが正式公開！詳細は[論文](https://arxiv.org/pdf/2505.15146)と[リーダーボード](https://huggingface.co/spaces/lmgame/game_arena_bench)をご確認ください。
- **[2025/3]** クラシックビデオゲームでゲームエージェントを構築し、各モデルをテスト。比較動画は[YouTubeチャンネル](https://www.youtube.com/channel/UCmuHTmXPhmqYlzNySc6woFw)で公開中！

## インストール

```bash
# リポジトリのクローン
git clone https://github.com/lmgame-org/GamingAgent.git
cd GamingAgent

# 仮想環境の作成と依存関係のインストール
conda create -n lmgame python==3.10 -y
conda activate lmgame
pip install -e .
```

## APIとモデル

### サポートモデル一覧

| プロバイダー | モデル |
|------------|--------|
| **OpenAI** | o4-mini, o3-mini, o3, o1, gpt-4o, gpt-4o-mini |
| **Anthropic** | claude-4-opus, claude-4-sonnet（思考モードあり）, claude-3-7-sonnet（思考モードあり）, claude-3-5-haiku, claude-3-5-sonnet |
| **Google** | gemini-2.5-pro, gemini-2.5-flash, gemini-2.0-flash-thinking-exp, gemini-2.0-pro, gemini-2.0-flash, gemini-1.5-pro |
| **xAI** | grok-3-mini |
| **Deepseek** | reasoner (R1), chat (V3) |
| **Qwen** | Qwen3 |

パフォーマンスの比較は[リーダーボード](https://huggingface.co/spaces/lmgame/game_arena_bench)で確認できます。

### APIキーの設定

`credentials.sh` にAPIキーを設定してください：

```bash
export OPENAI_API_KEY={YOUR_OPENAI_API_KEY}
export ANTHROPIC_API_KEY={YOUR_ANTHROPIC_API_KEY}
export GEMINI_API_KEY={YOUR_GEMINI_API_KEY}
export XAI_API_KEY={YOUR_XAI_API_KEY}
export DEEPSEEK_API_KEY={YOUR_DEEPSEEK_API_KEY}
```

```bash
source credentials.sh
```

> ⚠️ **高性能モデルの使用には高コストが発生する場合があります！**

### ローカルモデルのサポート

LLM Studio、vLLM、Modalによるローカル推論もサポートしています：

```bash
# LLM Studio（ポート1234）
python3 lmgame-bench/single_agent_runner.py \
  --game_name sokoban \
  --model_name llm-studio-Qwen/Qwen2.5-VL-32B-Instruct \
  --config_root_dir gamingagent/configs

# vLLM
python3 lmgame-bench/single_agent_runner.py \
  --game_name twenty_forty_eight \
  --model_name vllm-Qwen/Qwen2.5-32B-Instruct \
  --config_root_dir gamingagent/configs
```

## LMGame Bench

### セットアップ

#### Gymnasium環境

以下のゲームはインストール後すぐに実行可能です：

- **2048** (`twenty_forty_eight`)
- **Sokoban** (`sokoban`)
- **Candy Crush** (`candy_crush`)
- **Tetris** (`tetris`)

**Pokemon Red** の場合は追加でROMファイルが必要です：
```
gamingagent/configs/custom_06_pokemon_red/rom/pokemon.gb
```
エミュレータには[PyBoy](https://github.com/Baekalfen/PyBoy)を使用しています。

#### Retro環境

[stable-retro](https://github.com/Farama-Foundation/stable-retro)を使用したクラシックゲームの実行には、ゲームファイルを合法的に入手し以下でインポートする必要があります：

```bash
python3 -m retro.import /path/to/your/ROMs/directory/
```

現在サポートしているRetroゲーム：
- **Super Mario Bros 1985** (`super_mario_bros`)

stable-retroに含まれていない追加Retroゲーム（`retro.import`不要）：
- **Ace Attorney: Phoenix Wright** — ROMを `gamingagent/envs/retro_02_ace_attorney/AceAttorney-GbAdvance/` に配置

### 単一モデル評価

ゲームハーネスなしの単一モデルでの評価（ベンチマーク用）：

```bash
# 複数ゲームの並列評価
python3 lmgame-bench/run.py \
  --model_name {model_name} \
  --game_names sokoban,tetris,candy_crush,twenty_forty_eight \
  --harness_mode false

# 全モデル評価
bash lmgame-bench/evaluate_all.sh
```

### エージェント評価

ゲームハーネスあり（GamingAgentワークフロー）での評価：

```bash
python3 lmgame-bench/run.py \
  --model_name {model_name} \
  --game_names sokoban,tetris,candy_crush,twenty_forty_eight \
  --harness_mode true
```

#### コマンドオプション

| オプション | 説明 |
|----------|-----|
| `--harness_mode` | エージェントワークフロー使用有無。`"true"` / `"false"` / `"both"` |
| `--max_parallel_procs` | 並列実行の最大プロセス数 |
| `--game_names` | 評価対象ゲームのリスト（カンマ区切り） |

#### 設定のカスタマイズ

`run.py` は `single_agent_runner.py` の複数インスタンスを起動します。単一ゲーム・単一モデルの実行：

```bash
python3 lmgame-bench/single_agent_runner.py \
  --game_name {game_name} \
  --model_name {model_name} \
  --config_root_dir gamingagent/configs \
  [--harness]
```

ゲームエージェントの設定は `gamingagent/configs/{game_env_dir}/config.yaml` で調整できます。プロンプトは `gamingagent/configs/{game_env_dir}/module_prompts.json` にあります。

### ゲームパフォーマンスの分析

[lmgame_bench_evaluation colab](https://colab.research.google.com/drive/1CYFiJGm3EoBXXI8vICPVR82J9qrmmRvc#scrollTo=6ICtS7MjUMNG) または [評価ノートブック](eval/lmgame_Bench_Evaluation_Pipeline.ipynb) を使用して、論文の結果を再現できます。

生成したキャッシュディレクトリをColabワークスペースにアップロードすると、ベンチマーク結果との比較が可能です。

#### ゲームリプレイ動画の生成

Sokoban、2048、Tetris、Candy Crushのリプレイ動画を生成：

```bash
python eval/video_generation_script.py \
  --agent_config_path [CONFIG_PATH] \
  --episode_log_path [LOG_PATH] \
  --method text \
  --output_path [OUTPUT_NAME] \
  --fps 2
```

## Computer-Use Gaming Agents

PC・ラップトップ上で最新モデルをリアルタイムで動かすComputer-Use Gaming Agentをサポートしています。詳細は [computer_use](computer_use) を参照してください。

対応ゲーム：
- グリッドゲーム: 2048, Candy Crush, Sokoban, Tetris
- プラットフォーマー: Super Mario Bros
- ビジュアルノベル: Ace Attorney

## 独自ゲームの追加

### Gymnasium / Retro インターフェース

1. [Gymnasium](https://gymnasium.farama.org/introduction/create_custom_env/)（独自ゲーム実装）または [Stable Retro](https://retro.readthedocs.io/en/latest/integration.html)（クラシックゲーム）の手順に従ってゲーム環境を統合

2. `gamingagent/envs/` に環境実装を追加。観察生成とエージェントアクション処理メソッドを実装

3. `gamingagent/configs/` にゲームエージェント設定を追加

詳細は [gamingagent/envs](gamingagent/envs) を参照してください。

## 引用

このリポジトリが役立った場合は、以下の形式で引用してください：

```bibtex
@article{hu2025lmgame,
  title={lmgame-Bench: How Good are LLMs at Playing Games?},
  author={Hu, Lanxiang and Huo, Mingjia and Zhang, Yuxuan and Yu, Haoyang and Xing, Eric P and Stoica, Ion and Rosing, Tajana and Jin, Haojian and Zhang, Hao},
  journal={arXiv preprint arXiv:2505.15146},
  year={2025}
}
```
