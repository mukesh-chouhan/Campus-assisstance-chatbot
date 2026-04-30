"""Quick test for name extraction from queries"""
import re

def extract_name_from_message(text):
    """Extract person name from the user message, handling departments and titles."""
    faculty_id_match = re.search(r"\bIARE\s*(\d{4,})\b", text, flags=re.I)
    if faculty_id_match:
        return f"IARE{faculty_id_match.group(1)}"

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if re.search(r"\b(professor|prof|dr|doctor|mr|ms|mrs|madam|sir)\b", line, flags=re.I):
            line_clean = re.sub(r"\b(professor|prof|dr|doctor|mr|ms|mrs|madam|sir)\b\.?", "", line, flags=re.I)
            line_clean = re.sub(r"[^a-zA-Z\s]", " ", line_clean)
            line_clean = " ".join(w.strip() for w in line_clean.split() if w.strip())
            if 2 <= len(line_clean.split()) <= 5:
                return line_clean.strip()

    # Remove common query phrases
    t = re.sub(r"(tell me about|about|info on|information|details|who is|what is|profile of|show me|info|profile)", "", text, flags=re.I)
    
    # Remove titles
    t = re.sub(r"\b(professor|prof|dr|doctor|mr|ms|mrs|madam|sir)\b\.?", "", t, flags=re.I)
    
    # Remove department references (CSE, ECE, EEE, MECH, etc.) and variations
    t = re.sub(r"\b(cse|ece|eee|mech|civil|it|mechanical|electrical|electronics|computer science|cs|ec)\b", "", t, flags=re.I)
    t = re.sub(r"\(.*?\)", "", t)  # Remove anything in parentheses like (cs), (cse)
    t = re.sub(r"\bof\b", "", t, flags=re.I)  # Remove "of" preposition
    
    # Remove common stop words
    t = re.sub(r"\b(the|is|at|in|for|on|from|about|department|dept|faculty|staff)\b", "", t, flags=re.I)

    t = re.sub(r"\b(faculty id|designation|total experience|experience at iare|date of birth|email id|employment status|jntuh id|aicte faculty id|undergraduate degree|postgraduate degree|ph\.?d degree|areas of specialization|academic identity|video lectures|youtube link|vidwan link)\b", "", t, flags=re.I)
    
    # Clean up extra spaces
    name = " ".join([w.strip() for w in t.split() if w.strip()])
    return name.strip()

# Test cases
test_queries = [
    ("who is ramadevi of cse(cs)", "ramadevi"),
    ("tell me about prof ramadevi", "ramadevi"),
    ("Dr Ramadevi from CSE department", "Ramadevi"),
    ("who is ramadevi", "ramadevi"),
    ("show me ramadevi profile", "ramadevi"),
    ("info about Dr. Ramadevi G", "Ramadevi G"),
    ("professor ramadevi cse", "ramadevi"),
    ("Dr. G Ganapathi Rao details", "G Ganapathi Rao"),
    ("G Ganapathi Rao", "G Ganapathi Rao"),
    ("IARE11085 faculty details", "IARE11085"),
]

print("=" * 60)
print("NAME EXTRACTION TEST")
print("=" * 60)

failures = 0
for query, expected in test_queries:
    extracted = extract_name_from_message(query)
    print(f"\nQuery: {query}")
    print(f"Extracted Name: '{extracted}'")
    print(f"Expected: '{expected}'")

    if extracted.lower() != expected.lower():
        failures += 1
        print("Status: FAIL")
    else:
        print("Status: PASS")

if failures:
    raise AssertionError(f"Name extraction regressions found: {failures} failing cases")

print("\n" + "=" * 60)
print("All name extraction tests passed.")
