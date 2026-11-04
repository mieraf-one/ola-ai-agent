def is_anagram(s1: str, s2: str) -> bool:
    """Check if two strings are anagrams of each other.
    
    Case and whitespace are ignored.
    """
    clean_s1 = ''.join(s1.lower().split())
    clean_s2 = ''.join(s2.lower().split())
    return sorted(clean_s1) == sorted(clean_s2)
