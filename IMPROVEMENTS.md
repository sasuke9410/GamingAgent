# GamingAgent 未対応開発項目

このドキュメントは、未対応の開発課題・改善項目を優先度別に管理します。

---

## 📊 ステータス一覧

| # | 項目 | カテゴリ | 優先度 | ステータス |
|---|------|---------|--------|-----------|
| 1 | UI操作理解の強化（名前入力等） | Pokemon Red | 🔴 高 | ✅ 完了 |
| 2 | 思考言語の統一化 | Pokemon Red | 🔴 高 | ✅ 完了 |
| 3 | Ace Attorney WSL2実行 | Ace Attorney | 🔴 高 | ✅ 完了（ROM確認済） |
| 4 | ROM制御文字のフィルタリング | Pokemon Red | 🟡 中 | ✅ 完了 |
| 5 | Temperature設定の最適化 | Pokemon Red | 🟡 中 | ✅ 完了 |
| 6 | vLLMリモートサーバー対応 | インフラ | 🟡 中 | 未対応 |
| 7 | token_limit / reasoning_effort の設定化 | コアフレームワーク | 🟡 中 | 未対応 |
| 8 | Perceptionモジュールのテキスト処理 | コアフレームワーク | 🟡 中 | 未対応 |
| 9 | Tetrisワーカーの設定化 | Computer Use | 🟢 低 | 未対応 |
| 10 | TexasHoldemの対戦相手ポリシー拡張 | マルチエージェント | 🟢 低 | 未対応 |
| 11 | ゲーム固有知識のプロンプト追加 | Pokemon Red | 🟢 低 | ✅ 完了 |
| 12 | Sokobanレベル数の自動検出 | 環境 | 🟢 低 | 未対応 |

---

## 🔴 優先度：高

### 1. Pokemon Red — UI操作理解の強化

**問題**: 名前入力画面で文字選択方法を理解できていない。「A」ボタンを押し続けるだけで、方向キーで文字を選ぶ操作ができない。結果として「ア」→「アア」→「アアア」と同じ文字が連続入力される。

**影響**: ゲームの初期設定が完了できない。メニュー選択等の複雑なUI操作全般に影響。

**解決案**:
- **Option A（推奨）**: `module_prompts.json` にカナ入力操作の明示的な手順とfew-shot例を追加
- **Option B**: Perception Moduleでカーソル位置と選択可能文字のマッピングを生成し、エージェントに渡す

**担当ファイル**:
- `gamingagent/configs/custom_06_pokemon_red/module_prompts.json`
- `gamingagent/modules/perception_module.py`
- `gamingagent/envs/custom_06_pokemon_red/pokemon_red_env.py`

---

### 2. Pokemon Red — 思考言語の統一化

**問題**: エージェントの思考言語が不安定（英語→日本語→中国語と切り替わる）。ログの可読性低下とデバッグ困難を引き起こす。

**解決案**: 全モジュールのsystem promptに言語指定を追加。

```
System: You must think and respond in Japanese consistently throughout the entire game session.
```

**担当ファイル**:
- `gamingagent/configs/custom_06_pokemon_red/module_prompts.json`
- `gamingagent/configs/custom_06_pokemon_red/module_prompts_local_llm.json`

---

### 3. Ace Attorney — WSL2環境での実行完了

**問題**: Windows ネイティブでの stable-retro インストールは困難（依存関係の複雑さ）。WSL2ではインストール成功済みだが、以下の作業が残っている。

**現状**: WSL2に stable-retro 0.9.5 インストール済み。ROMファイルの配置と実行テストが未完了。

**残作業**:

```bash
# WSL2で実行
wsl

# ROMファイルをコピー
mkdir -p ~/GamingAgent/gamingagent/configs/retro_02_ace_attorney/rom
cp /mnt/c/Users/sasuke/Documents/GamingAgent/gamingagent/configs/retro_02_ace_attorney/rom/ace_attorney.gba \
   ~/GamingAgent/gamingagent/configs/retro_02_ace_attorney/rom/

# 依存関係インストール
cd ~/GamingAgent && pip3 install -e . --break-system-packages

# 実行テスト
python3 lmgame-bench/single_agent_runner.py \
  --game_name ace_attorney \
  --model_name claude-3-5-sonnet \
  --config_root_dir gamingagent/configs
```

**注意**: GUI表示が必要なため、WSLgまたはVcXsrvの設定が必要になる可能性あり。

---

## 🟡 優先度：中

### 4. Pokemon Red — ROM制御文字のフィルタリング

**問題**: ROM内の制御文字（ページ送り、メッセージボックス制御等）が文字化けして表示される（例: 「ごボゾグ」「ゲダざ」）。エージェントが誤情報を認識する可能性。

**担当ファイル**: `gamingagent/envs/custom_06_pokemon_red/pokemon_red_reader.py`

---

### 5. Pokemon Red — Temperature設定の最適化

**問題**: 思考言語の不安定性はTemperature設定が高すぎる可能性。現在設定なし（デフォルト値使用）。

**解決案**: `config.yaml` に `temperature: 0.3` 程度の値を追加。`tools/serving/api_manager.py` での受け渡しも確認が必要。

**担当ファイル**:
- `gamingagent/configs/custom_06_pokemon_red/config.yaml`
- `tools/serving/api_manager.py`

---

### 6. インフラ — vLLMリモートサーバー対応

**問題**: vLLMはlocalhostのみサポート。リモートvLLMサーバーへの接続が未実装。

**該当箇所** (`tools/serving/api_manager.py`):
- L505: `# TODO: support non-localhost vllm servers`
- L884, L1190: 同様のコメント（text_only / multimodal completion）

---

### 7. コアフレームワーク — token_limit / reasoning_effort の設定化

**問題**: `base_agent.py` でtoken_limitとreasoning_effortがハードコードされており、configから設定できない。

**該当箇所**:
- `gamingagent/agents/base_agent.py` L197, L265
- `gamingagent/modules/reasoning_module.py` L67（CoTモードの設定化）

---

### 8. コアフレームワーク — Perceptionモジュールのテキスト処理

**問題**: `perception_module.py` L146 でテキスト表現の処理ロジックが未実装（`# TODO: add textual representation processing logic`）。テキストのみ観察モードでの認知パイプライン使用時に影響。

**担当ファイル**: `gamingagent/modules/perception_module.py`

---

## 🟢 優先度：低

### 9. Computer Use Tetris — ワーカー設定の柔軟化

**問題**: 以下がハードコード。
- パッチの粒度（`workers.py` L136, L196）
- プランナーがthread 0固定（`workers.py` L360: `FIXME`）
- Tetrisエージェントのspeculator数（`tetris_agent.py` L66, L85）

---

### 10. マルチエージェント — TexasHoldemの対戦相手ポリシー拡張

**問題**: `TexasHoldemEnv.py` L354でランダムポリシーのみ実装。より強い対戦相手ポリシー（call-always、簡易ルールベース等）が未実装。

**担当ファイル**: `gamingagent/envs/zoo_02_texasholdem/TexasHoldemEnv.py`

---

### 11. Pokemon Red — ゲーム固有知識のプロンプト追加

**問題**: ゲームフロー（オープニング→名前入力→ポケモン選択）やUI操作パターンの知識が不足。

**担当ファイル**: `gamingagent/configs/custom_06_pokemon_red/module_prompts.json`

---

### 12. Sokoban環境 — レベル数の自動検出

**問題**: `sokobanEnv.py` L190で最大レベル数が `max_level = 6` にハードコード。`levels.txt` から自動検出すべき。

**担当ファイル**: `gamingagent/envs/custom_02_sokoban/sokobanEnv.py`

---

## ✅ 完了済み

| 項目 | 完了日 | 内容 |
|------|--------|-----|
| Pokemon Red: 思考言語統一化 | 2026-03-22 | 全モジュールsystem promptに日本語強制指示追加 |
| Pokemon Red: UI操作理解強化 | 2026-03-22 | カナグリッド操作手順・few-shot例をプロンプトに追加 |
| Pokemon Red: ROM制御文字フィルタ | 2026-03-22 | _convert_text()で未マップbyte（ゴミ文字）を無視するよう修正 |
| Pokemon Red: Temperature設定 | 2026-03-22 | config.yaml に temperature:0.3 追加、全モジュールスタックに伝播 |
| Pokemon Red: ゲーム固有知識追加 | 2026-03-22 | ゲームフロー・日本語ROMメニュー・バトルコマンドをプロンプトに追加 |
| Ace Attorney: ROM確認・WSL2手順整備 | 2026-03-22 | ROM存在確認済(8MB)、WSL2実行手順をACE_ATTORNEY_SETUP_STATUS.mdに記載 |
| Pokemon Red 日本語文字マッピング | 2025-03 | 日本語テキスト読み取りシステム実装 |
| LLM Studio ローカルモデル統合 | 2025-03 | vLLM/Modal/LLM Studio対応 |
| WSL2での stable-retro インストール | 2025-10 | WSL2環境でインストール成功 |

---

## 🔄 更新履歴

| 日付 | 更新内容 |
|------|---------|
| 2026-03-22 | Pokemon Red/Ace Attorney 全修正実装（温度設定・言語統一・UI操作・制御文字フィルタ等） |
| 2026-03-22 | コードTODO/FIXMEを含む全項目を整理・再構成 |
| 2025-10-12 | Ace Attorneyセットアップ状況を追記 |
| 2025-10-05 | 初版作成 |
