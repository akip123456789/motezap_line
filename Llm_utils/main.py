import re
import openai
from typing import Dict, List, Optional
import time
import os
from dotenv import load_dotenv
load_dotenv()

class QuestionClassifier:
    """
    テキストが疑問系か通常のメッセージかを効率よく判別するクラス
    低レイテンシーを実現するため、ルールベースの判定を優先し、
    必要に応じてAIを使用するハイブリッドアプローチを採用
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        初期化
        
        Args:
            openai_api_key: OpenAI APIキー（AI判定が必要な場合のみ）
        """
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        if openai_api_key:
            openai.api_key = os.environ.get("OPENAI_API_KEY")
        
        # 疑問詞パターン（日本語）
        self.question_words_jp = [
            '何', '誰', 'どこ', 'いつ', 'なぜ', 'どうして', 'どのように', 'どれ', 'どちら',
            'なに', 'だれ', 'いずれ', 'いかが', 'いかん', 'いかんせん'
        ]
        
        # 疑問詞パターン（英語）
        self.question_words_en = [
            'what', 'who', 'where', 'when', 'why', 'how', 'which', 'whose', 'whom'
        ]
        
        # 疑問符パターン
        self.question_patterns = [
            r'[？?]',  # 疑問符
            r'ですか\s*[？?]?',  # ですか
            r'でしょうか\s*[？?]?',  # でしょうか
            r'ますか\s*[？?]?',  # ますか
            r'でしょうか\s*[？?]?',  # でしょうか
            r'だろうか\s*[？?]?',  # だろうか
            r'かしら\s*[？?]?',  # かしら
            r'かな\s*[？?]?',  # かな
            r'^.*[？?]\s*$',  # 文末の疑問符
        ]
        
        # 英語の疑問文パターン
        self.english_question_patterns = [
            r'^(do|does|did|is|are|was|were|have|has|had|will|would|can|could|should|may|might)\s+',
            r'^(what|who|where|when|why|how|which|whose|whom)\s+',
            r'\?\s*$'
        ]
        
        # 確信度の閾値
        self.confidence_threshold = 0.8
        
    def is_question_by_rules(self, text: str) -> Dict[str, any]:
        """
        ルールベースで疑問系かどうかを判定
        
        Args:
            text: 判定対象のテキスト
            
        Returns:
            Dict: 判定結果と確信度を含む辞書
        """
        text = text.strip()
        if not text:
            return {'is_question': False, 'confidence': 0.0, 'method': 'empty'}
        
        confidence = 0.0
        reasons = []
        
        # 1. 疑問符のチェック
        if re.search(r'[？?]', text):
            confidence += 0.4
            reasons.append('疑問符あり')
        
        # 2. 日本語の疑問詞チェック
        for word in self.question_words_jp:
            if word in text:
                confidence += 0.3
                reasons.append(f'疑問詞「{word}」あり')
                break
        
        # 3. 英語の疑問詞チェック
        text_lower = text.lower()
        for word in self.question_words_en:
            if word in text_lower:
                confidence += 0.3
                reasons.append(f'疑問詞「{word}」あり')
                break
        
        # 4. 日本語の疑問文パターンチェック
        for pattern in self.question_patterns:
            if re.search(pattern, text):
                confidence += 0.2
                reasons.append('疑問文パターン一致')
                break
        
        # 5. 英語の疑問文パターンチェック
        for pattern in self.english_question_patterns:
            if re.search(pattern, text_lower):
                confidence += 0.3
                reasons.append('英語疑問文パターン一致')
                break
        
        # 6. 文末のイントネーションパターン（簡易版）
        if text.endswith(('か', 'の', 'ね', 'よ')):
            confidence += 0.1
            reasons.append('疑問的語尾')
        
        # 確信度を0-1の範囲に正規化
        confidence = min(confidence, 1.0)
        
        is_question = confidence >= 0.3  # 低い閾値で疑問系の可能性を判定
        
        return {
            'is_question': is_question,
            'confidence': confidence,
            'method': 'rules',
            'reasons': reasons
        }
    
    def is_question_by_ai(self, text: str) -> Dict[str, any]:
        """
        AIを使用して疑問系かどうかを判定
        
        Args:
            text: 判定対象のテキスト
            
        Returns:
            Dict: 判定結果と確信度を含む辞書
        """
        if not self.openai_api_key:
            return {'is_question': False, 'confidence': 0.0, 'method': 'no_api_key'}
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "あなたはテキストが疑問文かどうかを判定する専門家です。与えられたテキストが疑問文の場合は「はい」、そうでない場合は「いいえ」と答えてください。確信度も0-1の数値で示してください。"
                    },
                    {
                        "role": "user",
                        "content": f"以下のテキストが疑問文かどうか判定してください：\n{text}"
                    }
                ],
                max_tokens=50,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            
            # 結果の解析（簡易版）
            is_question = 'はい' in result or 'yes' in result.lower()
            confidence = 0.8 if is_question else 0.2  # 簡易的な確信度
            
            return {
                'is_question': is_question,
                'confidence': confidence,
                'method': 'ai',
                'raw_response': result
            }
            
        except Exception as e:
            return {
                'is_question': False,
                'confidence': 0.0,
                'method': 'ai_error',
                'error': str(e)
            }
    
    def classify(self, text: str, use_ai: bool = True) -> Dict[str, any]:
        """
        テキストが疑問系かどうかを判定するメイン関数
        
        Args:
            text: 判定対象のテキスト
            use_ai: AI判定を使用するかどうか
            
        Returns:
            Dict: 判定結果の詳細情報
        """
        start_time = time.time()
        
        # まずルールベースで判定
        rule_result = self.is_question_by_rules(text)
        
        # ルールベースの確信度が高い場合はAI判定をスキップ
        if rule_result['confidence'] >= self.confidence_threshold:
            processing_time = time.time() - start_time
            return {
                **rule_result,
                'processing_time': processing_time,
                'ai_used': False
            }
        
        # ルールベースの確信度が低い場合、AI判定を使用
        if use_ai and self.openai_api_key:
            print("AI判定を使用します。")
            ai_result = self.is_question_by_ai(text)
            processing_time = time.time() - start_time
            
            # AI判定が成功した場合はAI結果を採用（ルールベースより確信度が高い場合）
            if ai_result['method'] == 'ai' and ai_result['confidence'] > rule_result['confidence']:
                print("AI判定が成功した場合")
                return {
                    **ai_result,
                    'processing_time': processing_time,
                    'ai_used': True,
                    'rule_result': rule_result
                }
            # AI判定が失敗した場合や確信度が低い場合はルールベース結果を採用
            else:
                print("AI判定が失敗した場合")
                return {
                    **rule_result,
                    'processing_time': processing_time,
                    'ai_used': False,
                    'ai_result': ai_result
                }
        
        processing_time = time.time() - start_time
        return {
            **rule_result,
            'processing_time': processing_time,
            'ai_used': False
        }


def is_question(text: str, openai_api_key: Optional[str] = None, use_ai: bool = True) -> bool:
    """
    シンプルな疑問系判定関数（低レイテンシー重視）
    
    Args:
        text: 判定対象のテキスト
        openai_api_key: OpenAI APIキー（オプション）
        use_ai: AI判定を使用するかどうか
        
    Returns:
        bool: 疑問系の場合はTrue、そうでなければFalse
    """
    classifier = QuestionClassifier(openai_api_key)
    result = classifier.classify(text, use_ai)
    return result['is_question']


def classify_text_detailed(text: str, openai_api_key: Optional[str] = None, use_ai: bool = True) -> Dict[str, any]:
    """
    詳細な疑問系判定関数（デバッグ情報付き）
    
    Args:
        text: 判定対象のテキスト
        openai_api_key: OpenAI APIキー（オプション）
        use_ai: AI判定を使用するかどうか
        
    Returns:
        Dict: 判定結果の詳細情報
    """
    classifier = QuestionClassifier(openai_api_key)
    return classifier.classify(text, use_ai)

