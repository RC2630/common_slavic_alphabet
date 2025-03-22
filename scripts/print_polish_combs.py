def vowel_map(from_vowel: str) -> str:
    the_map: dict[str, str] = {"ą": "ǫ", "ó": "u"}
    return the_map[from_vowel] if from_vowel in the_map else from_vowel

def print_comb(from_letters: str, to_letters: str) -> None:
    print()
    for following_vowel in ("a", "ą", "e", "ę", "i", "o", "ó", "u", "y"):
        corrected_vowel: str = vowel_map(following_vowel)
        if following_vowel != "i":
            print(f"{from_letters}i{following_vowel} {to_letters}{corrected_vowel} polish")
        else:
            print(f"{from_letters}ii {to_letters}ji polish")

for from_letters, to_letters in (
    ("c", "ć"),
    ("dz", "dź"),
    ("n", "ń"),
    ("s", "ś"),
    ("z", "ź")
):
    print_comb(from_letters, to_letters)