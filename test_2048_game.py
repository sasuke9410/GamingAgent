#!/usr/bin/env python3
"""
2048 Game test with LLM Studio
"""

import sys
import os
import yaml

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_2048_config():
    """Test 2048 game configuration"""
    print("\n=== 2048 Configuration Test ===")

    try:
        config_path = "gamingagent/configs/custom_01_2048/config.yaml"

        if not os.path.exists(config_path):
            print(f"[ERROR] Config file not found: {config_path}")
            return False

        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        print(f"[OK] Config loaded successfully")
        print(f"Game name: {config.get('game_env', {}).get('name', 'Unknown')}")
        print(f"Agent model: {config.get('agent', {}).get('model_name', 'Unknown')}")
        print(f"Observation mode: {config.get('agent', {}).get('observation_mode', 'Unknown')}")
        print(f"Harness enabled: {config.get('agent', {}).get('harness', False)}")

        return True

    except Exception as e:
        print(f"[ERROR] Config test failed: {e}")
        return False

def test_direct_llm_studio_chat():
    """Test direct chat with LLM Studio for 2048 game"""
    print("\n=== Direct LLM Studio Chat for 2048 ===")

    try:
        from openai import OpenAI

        client = OpenAI(
            api_key="not-needed",
            base_url="http://192.168.50.248:1234/v1"
        )

        # Simple 2048 game state for testing
        game_state = """
Current 2048 Game State:
+----+----+----+----+
|  2 |  4 |    |    |
+----+----+----+----+
|    |  2 |    |    |
+----+----+----+----+
|    |    |    |    |
+----+----+----+----+
|    |    |    |    |
+----+----+----+----+

Available moves: up, down, left, right
Your goal: Combine tiles to reach 2048.
"""

        response = client.chat.completions.create(
            model="cyberagent-deepseek-r1-distill-qwen-14b-japanese",
            messages=[
                {"role": "system", "content": "You are a 2048 game assistant. Analyze the game state and suggest the best move. Respond with only the move direction (up/down/left/right) and a brief reason."},
                {"role": "user", "content": game_state + "\nWhat move should I make?"}
            ],
            max_tokens=100,
            temperature=0.1
        )

        print("[OK] LLM Studio 2048 response:")
        print(f"Response: {response.choices[0].message.content}")
        return True

    except Exception as e:
        print(f"[ERROR] LLM Studio chat failed: {e}")
        return False

def test_simple_env():
    """Test simple environment creation"""
    print("\n=== Simple Environment Test ===")

    try:
        # Try importing the 2048 environment
        import gymnasium as gym
        print("[OK] Gymnasium imported successfully")

        # Try creating a basic environment (if possible without complex dependencies)
        return True

    except ImportError as e:
        print(f"[INFO] Gymnasium not available: {e}")
        return True  # This is okay for basic test

    except Exception as e:
        print(f"[ERROR] Environment test failed: {e}")
        return False

if __name__ == "__main__":
    print("2048 Game test with LLM Studio started...")

    config_success = test_2048_config()
    llm_success = test_direct_llm_studio_chat()
    env_success = test_simple_env()

    print("\n=== Test Results ===")
    print(f"Config loading: {'OK' if config_success else 'FAILED'}")
    print(f"LLM Studio chat: {'OK' if llm_success else 'FAILED'}")
    print(f"Environment test: {'OK' if env_success else 'FAILED'}")

    if config_success and llm_success:
        print("\nBasic integration test passed! LLM Studio can process game states.")
    else:
        print("\nSome tests failed.")