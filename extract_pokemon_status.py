#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Pokemon Red ステータス抽出スクリプト"""

import json
import sys
import codecs

def extract_status(log_file, output_file):
    """ログからステータス情報を抽出してファイルに保存"""

    with codecs.open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    with codecs.open(output_file, 'w', encoding='utf-8') as out:
        out.write("=" * 80 + "\n")
        out.write("Pokemon Red 日本語ステータス詳細分析\n")
        out.write("=" * 80 + "\n\n")

        out.write(f"総ステップ数: {len(lines)}\n\n")

        # 最初の5ステップと最後の5ステップを分析
        steps_to_analyze = list(range(min(5, len(lines)))) + \
                          list(range(max(0, len(lines) - 5), len(lines)))
        steps_to_analyze = sorted(set(steps_to_analyze))

        for idx in steps_to_analyze:
            data = json.loads(lines[idx])
            info = data.get('info', {})

            out.write("=" * 80 + "\n")
            out.write(f"ステップ {data['step']}\n")
            out.write("=" * 80 + "\n\n")

            # 位置情報
            out.write("【位置情報】\n")
            out.write(f"  場所: {info.get('location', 'N/A')}\n")
            out.write(f"  座標: {info.get('coordinates', 'N/A')}\n")
            out.write(f"  移動可能方向: {info.get('valid_moves', 'N/A')}\n")
            out.write(f"  ステップ数: {info.get('steps', 'N/A')}\n\n")

            # ダイアログ（日本語）
            dialog = info.get('dialog', '')
            if dialog:
                out.write("【ダイアログ（日本語テキスト）】\n")
                # 改行を保持して表示
                dialog_lines = dialog.split('\n')
                for dline in dialog_lines[:10]:  # 最初の10行
                    out.write(f"  {dline}\n")
                if len(dialog_lines) > 10:
                    out.write(f"  ... (残り{len(dialog_lines) - 10}行)\n")
                out.write("\n")

            # エージェントの行動
            out.write("【エージェントの行動】\n")
            out.write(f"  選択: {data.get('agent_action', 'N/A')}\n\n")

            # エージェントの思考
            thought = data.get('thought', '')
            if thought:
                out.write("【エージェントの思考（日本語）】\n")
                thought_lines = thought.split('\n')
                for tline in thought_lines:
                    if tline.strip():
                        out.write(f"  {tline}\n")
                out.write("\n")

            # パフォーマンス
            out.write("【実行情報】\n")
            out.write(f"  報酬: {data.get('reward', 0)}\n")
            out.write(f"  スコア: {data.get('perf_score', 0)}\n")
            out.write(f"  処理時間: {data.get('time_taken_s', 0):.2f}秒\n")
            out.write(f"  終了: {data.get('terminated', False)}\n\n")

        # 全infoキーのサマリー
        out.write("\n" + "=" * 80 + "\n")
        out.write("利用可能な情報キー（最終ステップ）\n")
        out.write("=" * 80 + "\n\n")

        last_data = json.loads(lines[-1])
        last_info = last_data.get('info', {})

        for key in sorted(last_info.keys()):
            value = last_info[key]
            out.write(f"  {key}:\n")
            if isinstance(value, str) and len(value) > 100:
                out.write(f"    {value[:100]}...\n")
            elif isinstance(value, (dict, list)):
                out.write(f"    {json.dumps(value, ensure_ascii=False)[:200]}\n")
            else:
                out.write(f"    {value}\n")

if __name__ == "__main__":
    log_file = r"cache\pokemon_red\llm_studio_qwen\20251005_041232\episode_001_log.jsonl"
    output_file = "pokemon_status_analysis.txt"

    try:
        extract_status(log_file, output_file)
        print(f"分析完了: {output_file} に保存されました")
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
