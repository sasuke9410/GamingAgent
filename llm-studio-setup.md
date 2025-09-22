# LLM Studio 環境起動手順

## 前提条件

- Windows環境
- LLM Studio がインストール済み
- GamingAgent プロジェクトがクローン済み

## 起動手順

### 1. LLM Studio サーバーの起動

LLM Studio を起動し、以下の設定でサーバーを開始：

- **ポート**: 1234
- **ホスト**: localhost
- **API エンドポイント**: http://localhost:1234

### 2. 利用可能モデルの確認

```bash
curl http://localhost:1234/v1/models
```

確認済みの利用可能モデル：
- `cyberagent-deepseek-r1-distill-qwen-14b-japanese`
- `openai/gpt-oss-20b`
- `google/gemma-3-12b`
- `elyza-japanese-llama-2-13b-fast-instruct`
- `text-embedding-nomic-embed-text-v1.5`

### 3. 動作確認

#### 基本的な接続テスト
```bash
python -c "
import requests
import json

response = requests.post('http://localhost:1234/v1/chat/completions',
    headers={'Content-Type': 'application/json'},
    json={
        'model': 'cyberagent-deepseek-r1-distill-qwen-14b-japanese',
        'messages': [{'role': 'user', 'content': 'Hello, how are you?'}],
        'max_tokens': 50
    })
print('Status Code:', response.status_code)
if response.status_code == 200:
    print('LLM Studio is working!')
"
```

### 4. GamingAgent での使用方法

#### モデル名の指定形式
LLM Studio のモデルを使用する場合、モデル名の前に `llm-studio-` を付ける：

```bash
# 例: 単一ゲーム実行
python lmgame-bench/single_agent_runner.py \
  --game_name sokoban \
  --model_name llm-studio-cyberagent-deepseek-r1-distill-qwen-14b-japanese \
  --config_root_dir gamingagent/configs

# 例: 複数ゲーム実行
python lmgame-bench/run.py \
  --model_name llm-studio-cyberagent-deepseek-r1-distill-qwen-14b-japanese \
  --game_names sokoban,tetris,twenty_forty_eight
```

#### 推奨設定

**テキストベースゲーム用**（軽量モデル推奨）:
- 2048: `llm-studio-cyberagent-deepseek-r1-distill-qwen-14b-japanese`
- Sokoban: `llm-studio-cyberagent-deepseek-r1-distill-qwen-14b-japanese`
- Tetris: `llm-studio-cyberagent-deepseek-r1-distill-qwen-14b-japanese`

**ビジョンベースゲーム用**（マルチモーダルモデル必須）:
- Pokemon Red: マルチモーダル対応モデルが必要
- Super Mario Bros: マルチモーダル対応モデルが必要

### 5. 環境設定ファイル

APIManager 設定例：
```python
from tools.serving import APIManager

api_manager = APIManager(
    game_name="sokoban",
    llm_studio_host="localhost",
    llm_studio_port=1234,
    llm_studio_api_key="not-needed"
)
```

### 6. トラブルシューティング

#### 文字エンコーディングエラー
Windows環境でUnicodeエラーが発生する場合：
```python
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
```

#### 依存関係エラー
必要なパッケージが不足している場合：
```bash
# 仮想環境での依存関係インストール
pip install -e .
```

#### 接続エラー
LLM Studio サーバーが起動していない場合：
1. LLM Studio アプリケーションを確認
2. ポート 1234 が使用可能か確認
3. ファイアウォール設定を確認

### 7. パフォーマンス最適化

- **token_limit**: ローカルモデルの推論速度に応じて調整
- **batch_size**: システムリソースに応じて調整
- **concurrent_requests**: 1-2 に制限（ローカル環境）

## 注意事項

- ローカルモデルはクラウドAPIより推論速度が遅い場合があります
- GPU メモリ使用量に注意してモデルを選択してください
- 長時間の実行では定期的にメモリ使用量を監視してください