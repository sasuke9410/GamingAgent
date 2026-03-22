# GamingAgent 改善管理ドキュメント

このドキュメントは、GamingAgent システムで発見された課題と改善項目を管理します。

---

## 🎮 Pokemon Red 改善項目

### 優先度：高

#### 1. エージェント思考言語の統一化

**現状の問題**:

- エージェントの思考言語が不安定（英語 → 日本語 → 中国語 → 日本語と切り替わる）
- 特にステップ 5 で突然中国語に切り替わっている

**影響範囲**:

- ログの可読性低下
- デバッグの困難化
- エージェントの推論一貫性への懸念

**解決策**:

```yaml
# config.yamlに言語設定を追加
agent:
  language: "japanese" # または "english" で統一
  enforce_language: true
```

**プロンプト修正例**:

```
System: You must think and respond in Japanese consistently throughout the entire game session.
システム：ゲームセッション全体を通して、一貫して日本語で思考し応答してください。
```

**担当ファイル**:

- `gamingagent/configs/custom_06_pokemon_red/module_prompts.json`
- `gamingagent/configs/custom_06_pokemon_red/module_prompts_local_llm.json`

**ステータス**: 🔴 未対応

**更新日**: 2025-10-05

---

#### 2. UI 操作理解の強化（名前入力画面等）

**現状の問題**:

- 名前入力画面で文字選択方法を理解していない
- 「A」ボタンを押し続けるだけで、方向キーで文字を選ぶ操作ができていない
- 結果: 「ア」→「アア」→「アアア」と同じ文字が連続入力される

**影響範囲**:

- ゲームの初期設定が完了できない
- プレイヤー名を適切に入力できない
- メニュー選択等の複雑な UI 操作全般

**解決策**:

**Option 1: プロンプトに明示的な操作指示を追加**

```json
{
  "ui_operation_instructions": {
    "text_input_screen": {
      "description": "カナ入力画面では、方向キー（up/down/left/right）で文字を選択し、Aボタンで確定します。",
      "steps": [
        "1. 方向キーで目的の文字にカーソルを移動",
        "2. Aボタンで文字を選択・確定",
        "3. 「えんりょく」（完了）を選んで名前入力を終了"
      ]
    }
  }
}
```

**Option 2: Few-shot 例の追加**

```
Example:
現在の画面: カナ入力画面、カーソル位置「ア」、目標「サトシ」
思考: 「サ」を入力したいので、右に2回、下に1回移動する必要がある
行動: (right, 1)

現在の画面: カナ入力画面、カーソル位置「サ」
思考: 「サ」を確定する
行動: (a, 1)
```

**Option 3: 画面認識の強化**

- Perception Module で入力画面を検出
- カーソル位置と選択可能な文字のマッピングを提供
- エージェントに現在のカーソル位置と目標文字の情報を渡す

**担当ファイル**:

- `gamingagent/configs/custom_06_pokemon_red/module_prompts.json` (プロンプト修正)
- `gamingagent/modules/perception_module.py` (画面認識強化)
- `gamingagent/envs/custom_06_pokemon_red/pokemon_red_env.py` (UI 状態検出)

**ステータス**: 🔴 未対応

**更新日**: 2025-10-05

---

### 優先度：中

#### 3. ROM 制御文字のフィルタリング

**現状の問題**:

- ROM 内の制御文字（ページ送り、メッセージボックス制御等）が文字化けして表示される
- 例: 「ごボゾグ」「ゲダざ」等の意味不明な文字列

**影響範囲**:

- ダイアログの可読性低下
- エージェントが誤った情報を認識する可能性

**解決策**:

```python
# pokemon_red_reader.py に制御文字フィルタリングを追加
CONTROL_CHARACTERS = {
    0x00: '',  # 終端
    0x4F: '',  # ページ送り
    0x51: '',  # メッセージボックス制御
    # ... 他の制御文字
}

def filter_control_characters(text):
    """ROM制御文字を除去"""
    return ''.join(char for char in text if ord(char) not in CONTROL_CHARACTERS)
```

**担当ファイル**:

- `gamingagent/envs/custom_06_pokemon_red/pokemon_red_reader.py`

**ステータス**: 🔴 未対応

**更新日**: 2025-10-05

---

#### 4. Temperature 設定の最適化

**現状の問題**:

- 思考言語の不安定性は Temperature 設定が高すぎる可能性

**解決策**:

```yaml
# config.yamlに追加
agent:
  llm_parameters:
    temperature: 0.3 # デフォルト値より低めに設定
    top_p: 0.9
    top_k: 40
```

**担当ファイル**:

- `gamingagent/configs/custom_06_pokemon_red/config.yaml`
- `tools/serving.py` (APIManager)

**ステータス**: 🔴 未対応

**更新日**: 2025-10-05

---

### 優先度：低

#### 5. ゲーム固有知識のプロンプト追加

**現状の問題**:

- Pokemon Red 特有のゲームシステムや進行フローの知識が不足

**解決策**:

```json
{
  "pokemon_red_knowledge": {
    "game_flow": [
      "1. オープニング：オーク博士との会話",
      "2. 名前入力：プレイヤーとライバルの名前を入力",
      "3. 初期ポケモン選択：フシギダネ、ヒトカゲ、ゼニガメから1匹選択",
      "4. 冒険開始：マサラタウンから旅立ち"
    ],
    "common_ui_patterns": {
      "yes_no_dialog": "「はい」「いいえ」の選択肢では上下キーで選択、Aボタンで決定",
      "menu_navigation": "メニューでは上下キーで項目選択、Aボタンで決定、Bボタンでキャンセル"
    }
  }
}
```

**担当ファイル**:

- `gamingagent/configs/custom_06_pokemon_red/module_prompts.json`

**ステータス**: 🔴 未対応

**更新日**: 2025-10-05

---

## 🎯 Ace Attorney 改善項目

### 優先度：高

#### 1. stable-retro インストール自動化

**現状の問題**:

- Windows 環境で stable-retro のインストールが複雑
- CMake、Visual Studio Build Tools が必要
- エンコーディング問題（cp932 vs UTF-8）

**影響範囲**:

- Ace Attorney 環境が使用できない
- Retro 系ゲーム全般が動作しない

**解決策**:

**Option 1: WSL2 を使用**

```bash
# WSL2（Ubuntu）環境でインストール
sudo apt update
sudo apt install python3-pip cmake build-essential
pip install stable-retro
```

**Option 2: Docker コンテナ化**

```dockerfile
FROM python:3.10
RUN apt-get update && apt-get install -y cmake build-essential
RUN pip install stable-retro
# ... 他の依存関係
```

**Option 3: プリビルドバイナリの配布**

- CI/CD でビルド済み wheel を作成
- ユーザーは pip install で簡単にインストール

**担当ファイル**:

- `install_stable_retro.ps1` (改善)
- `Dockerfile` (新規作成)
- `.github/workflows/build-stable-retro.yml` (CI/CD)

**ステータス**: 🔴 未対応

**更新日**: 2025-10-05

---

## 📋 改善実施手順

### 1. 即座に対応可能な改善（優先度：高）

#### Pokemon Red: 思考言語の統一

1. `gamingagent/configs/custom_06_pokemon_red/module_prompts.json` を編集
2. 全てのモジュールの system prompt に言語指定を追加
3. テスト実行で言語の一貫性を確認

#### Pokemon Red: UI 操作指示の追加

1. `module_prompts.json` に操作ガイドを追加
2. Few-shot 例を 3-5 個追加
3. 名前入力画面での動作を確認

### 2. 中期的改善（1-2 週間）

#### Pokemon Red: 制御文字フィルタリング

1. `pokemon_red_reader.py` を解析
2. 制御文字マッピングテーブル作成
3. フィルタリング関数実装
4. テストケース追加

#### Ace Attorney: WSL2/Docker 対応

1. WSL2 環境で stable-retro インストール確認
2. Dockerfile 作成
3. ドキュメント更新

### 3. 長期的改善（1 ヶ月以上）

#### 画面認識の強化

1. Perception Module の改善設計
2. UI 要素検出の実装
3. 各ゲームでのテスト

---

## 📊 改善ステータス一覧

| 項目                | ゲーム       | 優先度 | ステータス | 担当者 | 期限 |
| ------------------- | ------------ | ------ | ---------- | ------ | ---- |
| 思考言語統一        | Pokemon Red  | 高     | 🔴 未対応  | -      | -    |
| UI 操作理解         | Pokemon Red  | 高     | 🔴 未対応  | -      | -    |
| 制御文字フィルタ    | Pokemon Red  | 中     | 🔴 未対応  | -      | -    |
| Temperature 最適化  | Pokemon Red  | 中     | 🔴 未対応  | -      | -    |
| ゲーム知識追加      | Pokemon Red  | 低     | 🔴 未対応  | -      | -    |
| stable-retro 自動化 | Ace Attorney | 高     | 🔴 未対応  | -      | -    |

**ステータス凡例**:

- 🔴 未対応
- 🟡 対応中
- 🟢 完了
- 🔵 検証中

---

## 🔄 更新履歴

| 日付       | 更新内容                                              | 更新者 |
| ---------- | ----------------------------------------------------- | ------ |
| 2025-10-05 | 初版作成、Pokemon Red / Ace Attorney の改善項目を記載 | Claude |

---

## 📝 メモ

- このドキュメントは定期的に更新してください
- 新しい課題が発見されたら即座に追加してください
- 改善が完了したらステータスを更新し、実装詳細を記録してください
- 優先度は状況に応じて柔軟に変更してください
