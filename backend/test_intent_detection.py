"""Test intent detection for person queries"""
import re

def detect_person_query(user_message):
    """Check if message is asking about a person"""
    person_query_patterns = [
        r'\bwho\s+is\b',
        r'\btell\s+me\s+about\b',
        r'\binfo\s+about\b',
        r'\bprofile\s+of\b',
        r'\bdetails\s+of\b'
    ]
    has_person_query = any(re.search(pattern, user_message, re.I) for pattern in person_query_patterns)
    
    has_title = re.search(r'\b(prof|professor|dr|doctor|mr|ms|mrs|madam|sir)\b', user_message, re.I)
    has_department = re.search(r'\b(cse|ece|eee|mech|civil|it|cs|ec|department|dept)\b', user_message, re.I)
    has_faculty_reference = re.search(r'\b(faculty|staff|professor|prof|teacher|hod|assistant professor|associate professor)\b', user_message, re.I)
    has_faculty_id = re.search(r'\bIARE\s*\d{4,}\b', user_message, re.I)

    profile_keyword_matches = re.findall(
        r'\b(designation|department|total\s+experience|experience\s+at\s+iare|date\s+of\s+birth|email\s*id|employment\s+status|jntuh\s+id|aicte\s+faculty\s+id|undergraduate\s+degree|postgraduate\s+degree|ph\.?d\s+degree|areas\s+of\s+specialization|academic\s+identity|video\s+lectures|vidwan|youtube)\b',
        user_message,
        re.I
    )
    has_profile_text_block = len(profile_keyword_matches) >= 2
    
    if has_person_query or (has_title and has_department) or has_faculty_id or (has_faculty_reference and (has_title or has_profile_text_block)):
        return True, 0.85
    return False, 0.0

# Test cases
test_queries = [
    ("who is ramadevi of cse(cs)", True),
    ("tell me about prof ramadevi", True),
    ("Dr Ramadevi from CSE department", True),
    ("who is ramadevi", True),
    ("show me all staff", False),
    ("faculty info", False),
    ("admission process", False),
    ("Dr. G Ganapathi Rao details", True),
    ("IARE11085 faculty details", True),
    (
        "Dr. G Ganapathi Rao Faculty ID IARE11085 Designation Assistant Professor Department CSE Data Science Total Experience 8 Years, 6 Months",
        True
    )
]

print("=" * 70)
print("INTENT DETECTION TEST")
print("=" * 70)

failures = 0
for query, expected in test_queries:
    is_person, confidence = detect_person_query(query)
    print(f"\nQuery: {query}")
    print(f"Is Person Query: {is_person}")
    print(f"Expected: {expected}")
    print(f"Confidence: {confidence}")
    print(f"Intent: {'faculty' if is_person else 'other'}")

    if is_person != expected:
        failures += 1
        print("Status: FAIL")
    else:
        print("Status: PASS")

if failures:
    raise AssertionError(f"Intent detection regressions found: {failures} failing cases")

print("\n" + "=" * 70)
print("All intent detection tests passed.")
