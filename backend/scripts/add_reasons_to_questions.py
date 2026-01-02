"""
Script to add 'reason' field to all questions in questions.json
This adds a placeholder that can be replaced with actual reasons later.
"""

import json
import os

def add_reasons_to_questions():
    """Add 'reason' field to all questions with placeholder text."""
    
    config_path = os.path.join(
        os.path.dirname(__file__), 
        '..', 
        'app', 
        'config', 
        'questions.json'
    )
    
    # Load current config
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Default reason text
    default_reason = "This information helps us understand your practice better and provide personalized support tailored to your needs."
    
    # Add reason to each question
    questions_updated = 0
    for stage in config['stages']:
        for question in stage['questions']:
            if 'reason' not in question or not question['reason']:
                question['reason'] = default_reason
                questions_updated += 1
    
    # Save updated config
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Updated {questions_updated} questions with default reasons")
    print(f"📝 File saved: {config_path}")
    print("\n💡 Next steps:")
    print("   1. Replace default reasons with specific explanations for each question")
    print("   2. Test the onboarding flow to see Karen explain 'why' when asked")

if __name__ == "__main__":
    add_reasons_to_questions()
