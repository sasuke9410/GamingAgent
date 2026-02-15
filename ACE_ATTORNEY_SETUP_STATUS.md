# Ace Attorney セットアップ状況レポート

**日付**: 2025-10-12
**目標**: `retro_02_ace_attorney` の実行環境構築

---

## 📊 現在の状況サマリー

### ✅ 完了した作業

1. **ROM ファイル確認 (Windows)**
   - ✅ `gamingagent/configs/retro_02_ace_attorney/rom/ace_attorney.gba` 存在確認済み
   - ✅ 設定ファイル `config.yaml` 確認済み

2. **Windows 環境での試行**
   - ✅ CMake インストール完了（winget経由）
   - ✅ Visual Studio 2022 Community インストール済み
   - ✅ stable-retro ソースコードダウンロード (v0.9.5)
   - ✅ setup.py パッチ作成（NMake Makefiles 対応）
   - ⚠️ **インストール失敗**: 依存関係不足（Python Development Module、ZLIB）

3. **WSL2 環境セットアップ**
   - ✅ WSL2 既にインストール済み（Ubuntu）
   - ✅ Python 3.12.3 利用可能
   - ✅ **stable-retro 0.9.5 インストール成功** 🎉
     - プリビルド wheel が利用可能で、一発でインストール完了
   - ✅ `~/GamingAgent` ディレクトリ既存確認

---

## ❌ 未完了の作業

### 高優先度

1. **ROM ファイルの WSL2 への配置**
   ```bash
   # Windows から WSL2 へ ROM ファイルをコピー
   mkdir -p ~/GamingAgent/gamingagent/configs/retro_02_ace_attorney/rom
   cp /mnt/c/Users/sasuke/Documents/GamingAgent/gamingagent/configs/retro_02_ace_attorney/rom/ace_attorney.gba \
      ~/GamingAgent/gamingagent/configs/retro_02_ace_attorney/rom/
   ```

2. **GamingAgent 依存関係インストール (WSL2)**
   ```bash
   cd ~/GamingAgent
   pip3 install -e . --break-system-packages
   ```

   または必要なパッケージのみ:
   ```bash
   pip3 install gymnasium pyglet farama-notifications --break-system-packages
   ```

3. **Ace Attorney 実行テスト**
   ```bash
   cd ~/GamingAgent
   python3 lmgame-bench/single_agent_runner.py \
     --game_name ace_attorney \
     --model_name claude-3-5-sonnet \
     --config_root_dir gamingagent/configs
   ```

### 中優先度

4. **API キー設定 (WSL2)**
   - `credentials.sh` をWSL2環境に配置
   - または環境変数を直接設定:
     ```bash
     export ANTHROPIC_API_KEY="your-key-here"
     ```

5. **X11 / ディスプレイ設定**
   - Ace Attorney は GUI ゲームのため、ディスプレイサーバーが必要
   - オプション:
     - **WSLg**: Windows 11 標準搭載（そのまま動作する可能性大）
     - **VcXsrv**: Windows 用 X サーバー
     - **ヘッドレスモード**: `DISPLAY` 設定なしで実行試行

---

## 🔍 技術的な課題と解決策

### Windows での stable-retro インストール問題

**問題点**:
- stable-retro の setup.py が Unix Makefiles をハードコード
- 依存関係（ZLIB、Python Development Module）の不足
- エンコーディング問題（cp932 vs UTF-8）

**解決策**:
- ✅ setup.py を NMake Makefiles 対応にパッチ
- ❌ 依存関係の完全解決は困難（vcpkg、手動ビルド等が必要）
- ✅ **WSL2 への移行が最適解**

### WSL2 での利点

- ✅ プリビルド wheel が利用可能（`manylinux_2_28_x86_64`）
- ✅ ビルドツール不要
- ✅ 1 コマンドでインストール完了
- ✅ Linux 環境で開発されたパッケージとの互換性が高い

---

## 📝 次のステップ

### すぐに実行可能なコマンド

```bash
# 1. WSL2 に入る
wsl

# 2. ROM ファイルをコピー
cd ~/GamingAgent
mkdir -p gamingagent/configs/retro_02_ace_attorney/rom
cp /mnt/c/Users/sasuke/Documents/GamingAgent/gamingagent/configs/retro_02_ace_attorney/rom/ace_attorney.gba \
   gamingagent/configs/retro_02_ace_attorney/rom/

# 3. 依存関係インストール
pip3 install -e . --break-system-packages

# 4. API キー設定（必要に応じて）
export ANTHROPIC_API_KEY="your-api-key"

# 5. Ace Attorney 実行
python3 lmgame-bench/single_agent_runner.py \
  --game_name ace_attorney \
  --model_name claude-3-5-sonnet \
  --config_root_dir gamingagent/configs
```

---

## 🛠️ トラブルシューティング

### ディスプレイエラーが出る場合

```bash
# WSLg が利用可能か確認
echo $DISPLAY

# 空の場合は設定
export DISPLAY=:0

# または X サーバーを Windows で起動して接続
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0
```

### stable-retro が ROM を認識しない場合

```bash
# ROM パスが正しいか確認
ls -lh ~/GamingAgent/gamingagent/configs/retro_02_ace_attorney/rom/ace_attorney.gba

# config.yaml の rom_path 設定確認
cat ~/GamingAgent/gamingagent/configs/retro_02_ace_attorney/config.yaml
```

### import エラーが出る場合

```bash
# 不足パッケージを個別インストール
pip3 install stable-retro gymnasium pyglet numpy --break-system-packages
```

---

## 📚 参考情報

### 関連ファイル

- **ROM**: `gamingagent/configs/retro_02_ace_attorney/rom/ace_attorney.gba`
- **設定**: `gamingagent/configs/retro_02_ace_attorney/config.yaml`
- **環境実装**: `gamingagent/envs/retro_02_ace_attorney/aceAttorneyEnv.py`
- **パッチ済み setup.py**: `stable-retro-0.9.5/setup.py` (Windows 側)

### インストール済みパッケージ (WSL2)

```
stable-retro==0.9.5
gymnasium==1.2.1
pyglet==1.5.31
numpy==2.3.3
cloudpickle==3.1.1
farama-notifications==0.0.4
```

### Windows 側の作業履歴

```powershell
# 作成されたスクリプト
- install_stable_retro.ps1      # 初期インストールスクリプト
- install_retro.ps1             # UTF-8 対応版
- install_retro_with_vs.ps1     # Visual Studio 環境セットアップ版
- install_patched_retro.ps1     # パッチ適用版
- test_cmake.ps1                # CMake テストスクリプト

# ログファイル
- install_log.txt
- vs_install_log.txt
- patched_install_log.txt
- cmake_error_log.txt
```

---

## ✨ 結論

**Windows ネイティブでの stable-retro インストールは困難**だが、**WSL2 では簡単にインストール可能**。

次のアクションは:
1. ROM ファイルを WSL2 にコピー
2. 依存関係をインストール
3. Ace Attorney を実行

これで Ace Attorney の実行環境が整います。
