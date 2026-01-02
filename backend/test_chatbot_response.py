"""
Test script to simulate FULL CONVERSATIONAL chatbot flow.
Shows how Karen asks questions, interprets answers, paraphrases, and continues.
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from langchain_openai import ChatOpenAI
from app.core.config import settings
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()


class ConversationalChatbotTester:
    """Test full conversational flow of the chatbot."""
    
    def __init__(self):
        """Initialize with OpenAI model."""
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            api_key=settings.openai_api_key,
            max_tokens=getattr(settings, 'openai_max_tokens', 2000)
        )
        # Load questions
        config_path = Path(__file__).parent / 'app' / 'config' / 'questions.json'
        with open(config_path, 'r', encoding='utf-8') as f:
            questions_config = json.load(f)
        self.questions = []
        for stage in questions_config['stages']:
            self.questions.extend(stage['questions'])
    
    def generate_contextual_question(self, question_text: str, last_response: str = None, step: int = 0):
        """Generate conversational question like Karen does."""
        if step == 0:
            return f"Great! Let's start with the basics. {question_text}"
        
        if not last_response:
            return question_text
        
        prompt = f"""You are Karen, a friendly AI assistant helping with practice onboarding.

The user just answered: "{last_response}"

Now you need to ask the next question: "{question_text}"

Create a natural, conversational way to ask this question that:
1. Briefly acknowledges/reacts to their previous answer (1 short sentence max)
2. Smoothly transitions to the new question
3. Keeps Karen's personality: warm, enthusiastic, professional but friendly
4. Uses emojis sparingly (0-1 per response)
5. Is concise - maximum 2-3 sentences total

Return ONLY the conversational question, nothing else."""

        try:
            response = self.llm.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            return question_text
    
    def interpret_response(self, question: str, user_response: str):
        """Interpret user response like the real system does - NO HARDCODED LOGIC."""
        # Check for skip
        skip_keywords = ['skip', 'pass', 'next']
        if any(keyword in user_response.lower() for keyword in skip_keywords):
            return {
                'valid': True,
                'type': 'SKIP',
                'data': '(Skipped)',
                'paraphrase': None
            }
        
        # Let AI handle EVERYTHING - including "why" questions
        interpretation_prompt = f"""You are Karen, a warm and professional AI assistant helping with healthcare practice onboarding.

Context: This is for official business records and system setup. While being conversational and friendly, you need complete, accurate information.

Question Asked: {question}
User's Response: {user_response}

Your task:
1. Determine if the response FULLY and APPROPRIATELY answers the question
   - For formal data (names, addresses, EINs): Require complete, proper information
   - Informal nicknames or incomplete answers should be redirected
   - If asking "why": Explain the specific business reason for this information, then re-ask
   - If off-topic: Acknowledge warmly but redirect firmly

2. Format your response as ONE of these:

UNDERSTOOD: [Friendly confirmation of their complete answer]
Example: "UNDERSTOOD: Perfect! Your full legal practice name is 'Healthy Smiles Dental Associates, LLC' - I've got that recorded! 😊"

EXPLAIN: [Personalized explanation of why this specific information is needed for their practice setup, then re-ask the question]
Example: "EXPLAIN: Great question! Your EIN is essential for us to properly set up your payment processing, insurance billing, and tax documentation in the system. This ensures everything runs smoothly from day one. So, what is your practice EIN?"

REDIRECT: [Acknowledge their input + explain what's specifically needed + re-ask]
Example: "REDIRECT: I appreciate you sharing that! However, for official records I need your complete legal name (first and last name). This will appear on all your practice documentation. What is your full legal name?"

Be professional yet warm. Explain the 'why' clearly when they ask. Be firm but friendly about needing complete information. Use 0-1 emoji max."""

        try:
            result = self.llm.invoke(interpretation_prompt)
            result_text = result.content.strip()
            
            if result_text.startswith("UNDERSTOOD:"):
                paraphrase = result_text.replace("UNDERSTOOD:", "").strip()
                return {
                    'valid': True,
                    'type': 'UNDERSTOOD',
                    'data': user_response,
                    'paraphrase': paraphrase
                }
            elif result_text.startswith("EXPLAIN:"):
                explanation = result_text.replace("EXPLAIN:", "").strip()
                return {
                    'valid': False,
                    'type': 'EXPLAIN',
                    'paraphrase': explanation
                }
            elif result_text.startswith("REDIRECT:"):
                redirect = result_text.replace("REDIRECT:", "").strip()
                return {
                    'valid': False,
                    'type': 'REDIRECT',
                    'paraphrase': redirect
                }
            else:
                return {
                    'valid': True,
                    'type': 'UNDERSTOOD',
                    'data': user_response,
                    'paraphrase': f"Got it! {user_response}"
                }
        except Exception as e:
            return {
                'valid': True,
                'type': 'UNDERSTOOD',
                'data': user_response,
                'paraphrase': "Thanks for sharing that!"
            }
    
    def simulate_conversation(self, test_responses: list):
        """
        Simulate a full conversation with multiple Q&A exchanges.
        
        Args:
            test_responses: List of user responses to test
        """
        print("\n" + "="*80)
        print("🎭 SIMULATING FULL CONVERSATIONAL ONBOARDING FLOW")
        print("="*80 + "\n")
        
        current_step = 0
        last_response = None
        conversation_history = []
        
        for i, user_input in enumerate(test_responses):
            if current_step >= len(self.questions):
                print("\n🎉 All test questions completed!\n")
                break
            
            current_question = self.questions[current_step]
            question_text = current_question['text']
            
            # Karen asks the question
            contextual_question = self.generate_contextual_question(
                question_text, 
                last_response,
                current_step
            )
            
            print(f"┌{'─'*78}┐")
            print(f"│ 🤖 KAREN (Question {current_step + 1}):                                                     │")
            print(f"└{'─'*78}┘")
            print(f"   {contextual_question}\n")
            
            # User responds
            print(f"┌{'─'*78}┐")
            print(f"│ 👤 USER:                                                                       │")
            print(f"└{'─'*78}┘")
            print(f"   {user_input}\n")
            
            # Karen interprets
            interpretation = self.interpret_response(question_text, user_input)
            
            if interpretation['valid']:
                # Karen paraphrases (if not skip)
                if interpretation['type'] != 'SKIP' and interpretation['paraphrase']:
                    print(f"┌{'─'*78}┐")
                    print(f"│ 🤖 KAREN (Confirmation):                                                      │")
                    print(f"└{'─'*78}┘")
                    print(f"   {interpretation['paraphrase']}\n")
                
                # Save answer and move to next question
                conversation_history.append({
                    'question': question_text,
                    'answer': interpretation['data'],
                    'paraphrase': interpretation.get('paraphrase')
                })
                
                last_response = interpretation['data']
                current_step += 1
                
                print(f"   ✅ Answer saved: {interpretation['data'][:50]}...\n")
            else:
                # Karen needs clarification
                print(f"┌{'─'*78}┐")
                print(f"│ 🤖 KAREN (Clarification needed):                                              │")
                print(f"└{'─'*78}┘")
                print(f"   {interpretation['paraphrase']}\n")
                print(f"   ⚠️  Answer NOT saved, waiting for valid response...\n")
            
            print("─" * 80 + "\n")
        
        # Summary
        print("\n" + "="*80)
        print("📊 CONVERSATION SUMMARY")
        print("="*80 + "\n")
        print(f"Total Questions Asked: {current_step}")
        print(f"Valid Answers Collected: {len(conversation_history)}")
        print(f"\nCollected Data:")
        for i, item in enumerate(conversation_history, 1):
            print(f"\n{i}. Q: {item['question']}")
            print(f"   A: {item['answer']}")
            if item['paraphrase']:
                print(f"   Karen's Confirmation: {item['paraphrase'][:60]}...")


def main():
    """Main test function."""
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║              CONVERSATIONAL CHATBOT FLOW SIMULATOR                         ║
║                                                                            ║
║  Simulates a real onboarding conversation with Karen                      ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)
    
    tester = ConversationalChatbotTester()
    
    # Simulate a CHALLENGING conversation with difficult responses
    print("\n🎯 TESTING DIFFICULT & EDGE CASE SCENARIOS\n")
    
    test_conversation = [
        # Q1: Name - completely off-topic
        "I'm not sure I want to share that yet",
        
        # Q1: Name - after redirect, gives vague answer
        "just call me Dr. J",
        
        # Q2: Birthday - talks about something related but doesn't answer
        "I love birthdays! They're so fun to celebrate",
        
        # Q2: Birthday - after redirect, finally answers
        "December 15",
        
        # Q3: Practice name - gives address instead
        "we're located on Main Street in Miami",
        
        # Q3: Practice name - after redirect, answers correctly
        "Staffless Practice",
        
        # Q4: EIN - gets defensive
        "that's personal information, why?",
        
        # Q4: EIN - after explanation, still deflects
        "I need to check with my accountant",
        
        # Q4: EIN - finally provides
        "12-3456789",
        
        # Q5: Office address - random story
        "my practice is really nice, we renovated last year",
        
        # Q5: Office address - after redirect
        "123 Main Street, Suite 100, Miami FL 33101",
        
        # Q6: Home address - philosophical response
        "home is where the heart is, you know?",
        
        # Q6: Home address - skip after being difficult
        "skip",
        
        # Q7: Phone - gives email instead
        "you can reach me at doc@staffless.com",
        
        # Q7: Phone - after redirect, correct
        "(305) 555-1234",
    ]
    
    tester.simulate_conversation(test_conversation)
    
    print("\n✅ Simulation complete!\n")


if __name__ == "__main__":
    main()
