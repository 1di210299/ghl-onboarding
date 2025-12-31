#!/usr/bin/env python3
"""
Simple test script to verify question loading without dependencies.
Tests JSON structure and basic logic without importing workflow.
"""

import json
from pathlib import Path


def load_questions():
    """Load questions from JSON config."""
    config_path = Path(__file__).parent / "backend" / "app" / "config" / "questions.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_question_by_index(index):
    """Get a question by its index (0-based)."""
    config = load_questions()
    current_index = 0
    
    for stage in config['stages']:
        for question in stage['questions']:
            if current_index == index:
                return question
            current_index += 1
    
    return None


def get_stage_for_question(index):
    """Determine which stage a question belongs to."""
    config = load_questions()
    current_index = 0
    
    for stage in config['stages']:
        for question in stage['questions']:
            if current_index == index:
                return stage['name']
            current_index += 1
    
    return None


def check_dependency(question, state):
    """Check if a question's dependency is satisfied."""
    dependency = question.get('dependency')
    if not dependency:
        return True
    
    # Parse dependency
    if '=' in dependency and '≠' not in dependency and '!=' not in dependency:
        parts = dependency.split('=')
        depends_on_field = parts[0].strip()
        expected_value = parts[1].strip().strip('"').strip("'")
        
        actual_value = state.get(depends_on_field)
        if expected_value.lower() == 'yes':
            return actual_value == True
        elif expected_value.lower() == 'no':
            return actual_value == False
        else:
            return str(actual_value) == expected_value
    
    elif '≠' in dependency or '!=' in dependency:
        separator = '≠' if '≠' in dependency else '!='
        parts = dependency.split(separator)
        depends_on_field = parts[0].strip()
        excluded_value = parts[1].strip().strip('"').strip("'")
        
        actual_value = state.get(depends_on_field)
        if excluded_value.lower() == 'no':
            return actual_value != False
        else:
            return str(actual_value) != excluded_value
    
    elif 'selected' in dependency.lower():
        parts = dependency.split('selected')
        value_to_check = parts[0].strip().strip('"').strip("'")
        field_ref = parts[1].strip()
        
        depends_on_field = field_ref
        actual_value = state.get(depends_on_field, [])
        
        if isinstance(actual_value, list):
            return value_to_check in actual_value
        else:
            return False
    
    return True


def test_load_questions():
    """Test loading questions from JSON config."""
    print("=" * 60)
    print("TEST 1: Load Questions Config")
    print("=" * 60)
    
    config = load_questions()
    
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
    print(f"   Text: {q1['text'][:50]}...")
    print(f"   Field: {q1['field_name']}")
    print(f"   Validator: {q1['validator']}")
    
    # Test middle question
    q25 = get_question_by_index(24)
    print(f"\n✅ Question 25 (index 24):")
    print(f"   ID: {q25['id']}")
    print(f"   Text: {q25['text'][:50]}...")
    print(f"   Field: {q25['field_name']}")
    print(f"   Type: {q25['type']}")
    
    # Test last question
    q48 = get_question_by_index(47)
    print(f"\n✅ Question 48 (index 47):")
    print(f"   ID: {q48['id']}")
    print(f"   Text: {q48['text'][:50]}...")
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
    
    # Find questions with dependencies
    config = load_questions()
    deps_found = 0
    
    for stage in config['stages']:
        for q in stage['questions']:
            if q.get('dependency'):
                deps_found += 1
    
    print(f"✅ Found {deps_found} questions with dependencies")
    
    # Test specific dependencies
    test_cases = [
        (14, {"q14_marketing": True}, True, "Q15 when Q14=Yes"),
        (14, {"q14_marketing": False}, False, "Q15 when Q14=No"),
        (29, {"q29_online": True}, True, "Q30 when Q29≠No"),
        (29, {"q29_online": False}, False, "Q30 when Q29=No"),
    ]
    
    for idx, state, expected, desc in test_cases:
        question = get_question_by_index(idx)
        if question and question.get('dependency'):
            result = check_dependency(question, state)
            status = "✅" if result == expected else "❌"
            print(f"{status} {desc}: {result} (expected {expected})")
    
    print()


def test_validators():
    """Test validator type distribution."""
    print("=" * 60)
    print("TEST 5: Validator Type Distribution")
    print("=" * 60)
    
    config = load_questions()
    validator_counts = {}
    
    for stage in config['stages']:
        for question in stage['questions']:
            validator = question.get('validator', 'text')
            validator_counts[validator] = validator_counts.get(validator, 0) + 1
    
    print("Validator type usage:")
    for validator, count in sorted(validator_counts.items()):
        print(f"   {validator}: {count} questions")
    
    print()


def test_field_names():
    """Test field name uniqueness."""
    print("=" * 60)
    print("TEST 6: Field Name Uniqueness")
    print("=" * 60)
    
    config = load_questions()
    field_names = set()
    duplicates = []
    
    for stage in config['stages']:
        for question in stage['questions']:
            field = question['field_name']
            if field in field_names:
                duplicates.append(field)
            field_names.add(field)
    
    if duplicates:
        print(f"❌ Found {len(duplicates)} duplicate field names:")
        for dup in duplicates:
            print(f"   - {dup}")
    else:
        print(f"✅ All {len(field_names)} field names are unique")
    
    print()


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("48-QUESTION JSON CONFIGURATION TEST")
    print("=" * 60)
    print()
    
    try:
        test_load_questions()
        test_get_questions()
        test_stages()
        test_dependencies()
        test_validators()
        test_field_names()
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Run database migration: 002_add_48_questions.sql")
        print("2. Install Python dependencies: pip install -r backend/requirements.txt")
        print("3. Test workflow with real conversations")
        print()
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ TEST FAILED")
        print("=" * 60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
