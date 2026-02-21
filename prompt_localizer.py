"""
Prompt localization helper for Pokemon Red AI system
"""
from config_loader import config

class PromptLocalizer:
    """Localize prompts based on language settings from .env file"""

    def __init__(self):
        self.language = config.get_model_output_language()

    def get_language_suffix(self) -> str:
        """Get language instruction suffix for prompts"""
        if self.language == 'JP':
            return "\n\n重要な指示: 全ての回答を日本語で出力してください。ゲームの分析、思考プロセス、行動の説明を日本語で行ってください。"
        return ""  # English is default

    def get_reasoning_system_prompt(self) -> str:
        """Get localized reasoning module system prompt"""
        base_prompt = "You are an AI assistant playing Pokemon Red. Your goal is to become the Pokemon Champion by progressing through the game, catching Pokemon, and defeating gym leaders and the Elite Four.\n\nI want your response to be formatted as follows:\nthought: [Your reasoning about the game state and strategy]\nmove: (action_name, repeat_count)\n\nWhere action_name must be one of the available Pokemon Red actions and repeat_count is how many times to execute this action (usually 1, but can be 2-3 for movement to speed up navigation)."

        if self.language == 'JP':
            jp_prompt = "あなたはポケットモンスター赤をプレイするAIアシスタントです。ジムリーダーと四天王を倒してポケモンチャンピオンになることが目標です。\n\n回答は以下の形式で出力してください:\nthought: [ゲーム状況と戦略についての思考プロセスを日本語で]\nmove: (action_name, repeat_count)\n\naction_nameは利用可能なポケモン赤のアクション名、repeat_countは実行回数（通常1、移動の場合は2-3回で高速化可能）です。"
            return jp_prompt + self.get_language_suffix()

        return base_prompt

    def get_perception_system_prompt(self) -> str:
        """Get localized perception module system prompt"""
        base_prompt = "You are a Pokemon Red Perception AI. Your task is to analyze the game state (either from an image or textual description) and return a structured JSON representation. Do not suggest moves or actions."

        if self.language == 'JP':
            jp_prompt = "あなたはポケットモンスター赤の認識AIです。ゲーム状態（画像またはテキスト記述）を分析し、構造化されたJSON表現を返すことが任務です。行動や移動の提案は行わないでください。"
            return jp_prompt + self.get_language_suffix()

        return base_prompt

    def get_memory_reflection_system_prompt(self) -> str:
        """Get localized memory reflection system prompt"""
        base_prompt = "You are the memory module of a Pokemon Red-playing AI that provides strategic reflections on game progress and important events. You help maintain awareness of important gameplay patterns and provide strategic guidance."

        if self.language == 'JP':
            jp_prompt = "あなたはポケットモンスター赤をプレイするAIのメモリモジュールです。ゲーム進行と重要な出来事について戦略的な振り返りを行います。重要なゲームプレイパターンの認識を維持し、戦略的なガイダンスを提供します。"
            return jp_prompt + self.get_language_suffix()

        return base_prompt

# Global localizer instance
localizer = PromptLocalizer()