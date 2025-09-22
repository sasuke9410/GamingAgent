#!/usr/bin/env python3
"""
LLM Studio APIManager接続テスト
"""

import sys
import os

# プロジェクトルートをPythonパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from tools.serving.api_manager import APIManager
    print("[OK] APIManager正常にインポートされました")
except ImportError as e:
    print(f"[ERROR] APIManagerのインポートに失敗: {e}")
    sys.exit(1)

def test_llm_studio_connectivity():
    """LLM Studio接続テスト"""
    print("\n=== LLM Studio接続テスト ===")

    # APIManagerインスタンス作成
    try:
        api_manager = APIManager(
            game_name="test",
            llm_studio_host="192.168.50.248",
            llm_studio_port=1234,
            llm_studio_api_key="not-needed",
            enable_logging=False  # テスト時はログ無効
        )
        print("[OK] APIManagerインスタンス作成成功")
    except Exception as e:
        print(f"✗ APIManagerインスタンス作成失敗: {e}")
        return False

    # テキスト完了テスト
    print("\n--- テキスト完了テスト ---")
    try:
        model_name = "llm-studio-cyberagent-deepseek-r1-distill-qwen-14b-japanese"
        system_prompt = "あなたは役立つアシスタントです。日本語で回答してください。"
        prompt = "こんにちは！元気ですか？"

        print(f"モデル: {model_name}")
        print(f"プロンプト: {prompt}")

        result, costs = api_manager.text_only_completion(
            model_name=model_name,
            system_prompt=system_prompt,
            prompt=prompt,
            temperature=0.7,
            token_limit=100
        )

        print(f"✓ LLM Studio応答成功:")
        print(f"応答: {result}")
        print(f"コスト情報: {costs}")
        return True

    except Exception as e:
        print(f"✗ LLM Studio呼び出し失敗: {e}")
        return False

def test_direct_openai_call():
    """OpenAIクライアント直接呼び出しテスト"""
    print("\n=== OpenAIクライアント直接テスト ===")

    try:
        from openai import OpenAI

        client = OpenAI(
            api_key="not-needed",
            base_url="http://192.168.50.248:1234/v1"
        )

        response = client.chat.completions.create(
            model="cyberagent-deepseek-r1-distill-qwen-14b-japanese",
            messages=[
                {"role": "system", "content": "あなたは役立つアシスタントです。"},
                {"role": "user", "content": "1+1は何ですか？"}
            ],
            max_tokens=50,
            temperature=0.1
        )

        print("✓ OpenAIクライアント直接呼び出し成功:")
        print(f"応答: {response.choices[0].message.content}")
        return True

    except Exception as e:
        print(f"✗ OpenAIクライアント呼び出し失敗: {e}")
        return False

if __name__ == "__main__":
    print("LLM Studio疎通確認テスト開始...")

    # 直接呼び出しテスト
    direct_success = test_direct_openai_call()

    # APIManagerテスト
    api_manager_success = test_llm_studio_connectivity()

    print("\n=== テスト結果 ===")
    print(f"OpenAI直接呼び出し: {'✓ 成功' if direct_success else '✗ 失敗'}")
    print(f"APIManager呼び出し: {'✓ 成功' if api_manager_success else '✗ 失敗'}")

    if direct_success and api_manager_success:
        print("\n🎉 すべてのテストが成功しました！LLM Studioとの統合は正常に動作しています。")
    else:
        print("\n❌ 一部のテストが失敗しました。")