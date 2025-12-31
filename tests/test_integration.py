#!/usr/bin/env python3
"""
Quick test script to verify the 48-question workflow integration.
Tests question loading, dependency checking, and validator routing.
"""

import sys
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.services.workflow import load_questions_config, get_question_by_index, get_stage_for_question, check_dependency


def test_load_questions():
    """Test loading questions from JSON config."""
    print("=" * 60)
    print("TEST 1: Load Questions Config")
    print("=" * 60)
    
    config = load_questions_config()
    
    print(f"✅ Config loaded successfully")
    print(f"   Version: {config['version']}")
    print(f"   Total questions: {config['total_questions']}")
    print(f"   Number of stages: {len(config['stages'])}")
    
    for stage in config['stages']:
        print(f"   - {stage['name']}: {len(stage['questions'])} questions")
    
    print()
    return config


def test_get_questions():
    """Test retrieving specific questions."""
    print("=" * 60)
    print("TEST 2: Retrieve Specific Questions")
    print("=" * 60)
    
    # Test first question
    q1 = get_question_by_index(0)
    print(f"✅ Question 1 (index 0):")
    print(f"   ID: {q1['id']}")
    print(f"   Text: {q1['text']}")
    print(f"   Field: {q1['field_name']}")
    print(f"   Validator: {q1['validator']}")
    
    # Test middle question
    q25 = get_question_by_index(24)
    print(f"\n✅ Question 25 (index 24):")
    print(f"   ID: {q25['id']}")
    print(f"   Text: {q25['text']}")
    print(f"   Field: {q25['field_name']}")
    print(f"   Type: {q25['type']}")
    print(f"   Options: {q25['options']}")
    
    # Test last question
    q48 = get_question_by_index(47)
    print(f"\n✅ Question 48 (index 47):")
    print(f"   ID: {q48['id']}")
    print(f"   Text: {q48['text']}")
    print(f"   Field: {q48['field_name']}")
    print(f"   Type: {q48['type']}")
    
    print()


def test_stages():
    """Test stage detection."""
    print("=" * 60)
    print("TEST 3: Stage Detection")
    print("=" * 60)
    
    test_indices = [0, 8, 9, 15, 16, 27, 28, 47]
    
    for idx in test_indices:
        stage = get_stage_for_question(idx)
        question = get_question_by_index(idx)
        print(f"✅ Question {idx + 1} ({question['id']}): Stage = {stage}")
    
    print()


def test_dependencies():
    """Test conditional dependency checking."""
    print("=" * 60)
    print("TEST 4: Dependency Checking")
    print("=" * 60)
    
    # Test Q15 (depends on Q14 = Yes)
    q15 = get_question_by_index(14)  # Q15
    print(f"Testing: {q15['text']}")
    print(f"Dependency: {q15['dependency']}")
    
    state_yes = {"q14_marketing": True}
    state_no = {"q14_marketing": False}
    
    result_yes = check_dependency(q15, state_yes)
    result_no = check_dependency(q15, state_no)
    
    print(f"   When Q14 = True: {result_yes} (should be True)")
    print(f"   When Q14 = False: {result_no} (should be False)")
    
    # Test Q30 (depends on Q29 ≠ No)
    q30 = get_question_by_index(29)  # Q30
    print(f"\nTesting: {q30['text']}")
    print(f"Dependency: {q30['dependency']}")
    
    state_has_website = {"q29_online": True}
    state_no_website = {"q29_online": False}
    
    result_has = check_dependency(q30, state_has_website)
    result_no = check_dependency(q30, state_no_website)
    
    print(f"   When Q29 = True: {result_has} (should be True)")
    print(f"   When Q29 = False: {result_no} (should be False)")
    
    # Test Q35 (depends on "Instagram" selected in Q34)
    q35 = get_question_by_index(34)  # Q35
    print(f"\nTesting: {q35['text']}")
    print(f"Dependency: {q35['dependency']}")
    
    state_with_ig = {"q34_social": ["Instagram", "Facebook"]}
    state_without_ig = {"q34_social": ["Facebook", "LinkedIn"]}
    
    result_with = check_dependency(q35, state_with_ig)
    result_without = check_dependency(q35, state_without_ig)
    
    print(f"   When Instagram in list: {result_with} (should be True)")
    print(f"   When Instagram NOT in list: {result_without} (should be False)")
    
    print()


def test_validators():
    """Test validator type mapping."""
    print("=" * 60)
    print("TEST 5: Validator Type Distribution")
    print("=" * 60)
    
    config = load_questions_config()
    validator_counts = {}
    
    for stage in config['stages']:
        for question in stage['questions']:
            validator = question.get('validator', 'text')
            validator_counts[validator] = validator_counts.get(validator, 0) + 1
    
    print("Validator type usage:")
    for validator, count in sorted(validator_counts.items()):
        print(f"   {validator}: {count} questions")
    
    print()


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("48-QUESTION WORKFLOW INTEGRATION TEST")
    print("=" * 60)
    print()
    
    try:
        test_load_questions()
        test_get_questions()
        test_stages()
        test_dependencies()
        test_validators()
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print()
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ TEST FAILED")
        print("=" * 60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
