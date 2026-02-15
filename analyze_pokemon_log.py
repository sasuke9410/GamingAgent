#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Pokemon Red ログ分析スクリプト - 日本語ステータス確認"""

import json
import sys

def analyze_pokemon_log(log_file):
    """ログファイルを分析して日本語処理とステータス取得を確認"""

    print("=" * 80)
    print("Pokemon Red 日本語ステータス分析レポート")
    print("=" * 80)
    print()

    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print(f"総ステップ数: {len(lines)}")
    print()

    # 各ステップを分析
    for i, line in enumerate(lines[:10], 1):  # 最初の10ステップを分析
        data = json.loads(line)

        print(f"{'=' * 80}")
        print(f"ステップ {data['step']}")
        print(f"{'=' * 80}")

        # ゲーム情報
        info = data.get('info', {})

        print(f"\n【位置情報】")
        print(f"  場所: {info.get('location', 'N/A')}")
        print(f"  座標: {info.get('coordinates', 'N/A')}")
        print(f"  移動可能方向: {info.get('valid_moves', 'N/A')}")

        # 日本語ダイアログ
        dialog = info.get('dialog', '')
        if dialog:
            print(f"\n【ダイアログ（生データ）】")
            # 最初の200文字のみ表示
            print(f"  {dialog[:200]}")
            if len(dialog) > 200:
                print(f"  ... (全{len(dialog)}文字)")

        # エージェントの行動
        print(f"\n【エージェントの行動】")
        print(f"  選択した行動: {data.get('agent_action', 'N/A')}")

        # エージェントの思考（日本語）
        thought = data.get('thought', '')
        print(f"\n【エージェントの思考】")
        if thought:
            # 改行で分割して表示
            thought_lines = thought.split('\n')
            for tline in thought_lines[:5]:  # 最初の5行
                if tline.strip():
                    print(f"  {tline[:150]}")
                    if len(tline) > 150:
                        print(f"    ...")

        # パフォーマンス情報
        print(f"\n【実行情報】")
        print(f"  報酬: {data.get('reward', 0)}")
        print(f"  パフォーマンススコア: {data.get('perf_score', 0)}")
        print(f"  処理時間: {data.get('time_taken_s', 0):.2f}秒")
        print(f"  終了フラグ: {data.get('terminated', False)}")

        print()

    # メモリモジュール分析
    print("\n" + "=" * 80)
    print("詳細ステータス分析（最後のステップ）")
    print("=" * 80)

    last_data = json.loads(lines[-1])
    last_info = last_data.get('info', {})

    # すべてのキーを表示
    print(f"\n【利用可能な情報キー】")
    for key in sorted(last_info.keys()):
        print(f"  - {key}")

    print(f"\n【詳細情報】")
    for key, value in sorted(last_info.items()):
        if key == 'dialog':
            print(f"\n  {key}:")
            print(f"    {str(value)[:300]}")
        elif isinstance(value, (dict, list)):
            print(f"\n  {key}:")
            print(f"    {json.dumps(value, ensure_ascii=False, indent=4)[:500]}")
        else:
            print(f"  {key}: {value}")

if __name__ == "__main__":
    log_file = sys.argv[1] if len(sys.argv) > 1 else \
        r"cache\pokemon_red\llm_studio_qwen\20251005_041232\episode_001_log.jsonl"

    analyze_pokemon_log(log_file)
