from io import TextIOWrapper as File
from typing import Callable, Any

class Language:

    def __init__(self, lang: str, script: str, description: str):
        self.lang: str = lang
        self.script: str = script
        self.description: str = description

    def __repr__(self) -> str:
        return "{" + f"lang: \"{self.lang}\", script: \"{self.script}\", desc: \"{self.description}\"" + "}"

    def __str__(self) -> str:
        return self.__repr__()

INPUT_FILE: str = "transliteration/input.txt"
OUTPUT_FILE: str = "transliteration/output.txt"
CYRILLIC_DEFAULT_FILE: str = "mappings/cyrillic_default.txt"
CYRILLIC_SPECIFIC_FILE: str = "mappings/language_specific_cyrillic.txt"
LATIN_SPECIFIC_FILE: str = "mappings/language_specific_latin.txt"
UPPER_LOWER_FILE: str = "mappings/uppercase_lowercase.txt"
CHOICE_TO_LANGUAGE_FILE: str = "mappings/choice_lang_script.txt"
CASE_SCENARIO_FILE: str = "mappings/case_scenarios.txt"
VOWELS_FILE: str = "lists/vowels.txt"

MAX_MAPPING_LENGTH: int = -1

CYRILLIC_DEFAULT_MAP: dict[int, dict[str, str]] = {}
CYRILLIC_SPECIFIC_MAP: dict[int, dict[str, dict[str, str]]] = {}
LATIN_SPECIFIC_MAP: dict[int, dict[str, dict[str, str]]] = {}
UPPER_TO_LOWER_MAP: dict[str, str] = {}
LOWER_TO_UPPER_MAP: dict[str, str] = {}
CHOICE_TO_LANGUAGE_MAP: dict[int, Language] = {}
CASE_SCENARIO_MAP: dict[tuple[str, str, str], Callable[[str], str]] = {}

VOWELS_LIST: list[str] = []

def readFileAndSplitByLineAndSpace(filename: str) -> list[list[str]]:
    file: File = open(filename, "r", encoding = "utf-8")
    content: list[str] = file.read().split("\n")
    file.close()
    return [line.split(" ") for line in content]

def initializeVowelList() -> None:
    global VOWELS_LIST
    file: File = open(VOWELS_FILE, "r", encoding = "utf-8")
    content: list[str] = file.read().split("\n")
    file.close()
    VOWELS_LIST = content

def getMaxMappingLengthFromContent(content: list[list[str]]) -> int:
    global MAX_MAPPING_LENGTH
    lengths: list[int] = [len(entry[0]) for entry in content]
    maxLength: int = max(lengths)
    MAX_MAPPING_LENGTH = max(MAX_MAPPING_LENGTH, maxLength)
    return maxLength

def initializeDictToMaxLength(d: dict[int, dict[Any, Any]], maxLength: int) -> None:
    for i in range(1, maxLength + 1):
        d[i] = {}

def initializeUpperLowerMaps() -> None:
    content: list[list[str]] = readFileAndSplitByLineAndSpace(UPPER_LOWER_FILE)
    for entry in content:
        UPPER_TO_LOWER_MAP[entry[0]] = entry[1]
        LOWER_TO_UPPER_MAP[entry[1]] = entry[0]

def initializeCyrillicDefaultMap() -> None:
    content: list[list[str]] = readFileAndSplitByLineAndSpace(CYRILLIC_DEFAULT_FILE)
    initializeDictToMaxLength(CYRILLIC_DEFAULT_MAP, getMaxMappingLengthFromContent(content))
    for entry in content:
        CYRILLIC_DEFAULT_MAP[len(entry[0])][entry[0]] = entry[1]

def initializeSpecificMap(specificMap: dict[int, dict[str, dict[str, str]]], specificFilename: str) -> None:
    
    content: list[list[str]] = readFileAndSplitByLineAndSpace(specificFilename)
    initializeDictToMaxLength(specificMap, getMaxMappingLengthFromContent(content))
    
    for entry in content:

        mapFrom: str = entry[0]
        mapTo: str = entry[1]
        mapLangs: list[str] = entry[2:]
        currLenMap: dict[str, dict[str, str]] = specificMap[len(mapFrom)]

        for lang in mapLangs:
            if lang not in currLenMap:
                currLenMap[lang] = {}
            currLenMap[lang][mapFrom] = mapTo

def initializeChoiceToLangMap() -> None:
    content: list[list[str]] = readFileAndSplitByLineAndSpace(CHOICE_TO_LANGUAGE_FILE)
    for i in range(len(content)):
        entry: list[str] = content[i]
        description: str = " ".join(entry[2:])
        CHOICE_TO_LANGUAGE_MAP[i + 1] = Language(entry[0], entry[1], description)

# returns one of {"lowercase", "uppercase", "neither"}
def getCase(character: str) -> str:
    if character in LOWER_TO_UPPER_MAP:
        return "lowercase"
    elif character in UPPER_TO_LOWER_MAP:
        return "uppercase"
    else:
        return "neither"
    
# returns one of {"lowercase", "uppercase", "sentence"}
def getCaseType(s: str) -> str:
    if len(s) == 1:
        return "uppercase" if getCase(s) == "uppercase" else "lowercase"
    elif len(s) >= 2:
        firstCharacterType: str = getCaseType(s[0])
        secondCharacterType: str = getCaseType(s[1])
        if firstCharacterType == "uppercase" and secondCharacterType == "uppercase":
            return "uppercase"
        elif firstCharacterType == "lowercase" and secondCharacterType == "lowercase":
            return "lowercase"
        elif firstCharacterType == "uppercase" and secondCharacterType == "lowercase":
            return "sentence"
        else:
            return "lowercase" # this scenario is assumed to never occur
    else:
        raise RuntimeError("cannot be used on empty string")
    
def toLowerCase(s: str) -> str:
    return "".join([UPPER_TO_LOWER_MAP.get(c, c) for c in s])
    
def toUpperCase(s: str) -> str:
    return "".join([LOWER_TO_UPPER_MAP.get(c, c) for c in s])
    
def toSentenceCase(s: str) -> str:
    firstChar: str = toUpperCase(s[0])
    restChars: str = toLowerCase(s[1:])
    return firstChar + restChars

def initializeCaseScenarioMap() -> None:
    content: list[list[str]] = readFileAndSplitByLineAndSpace(CASE_SCENARIO_FILE)
    for entry in content:
        scenario: tuple[str, str, str] = (entry[0], entry[1], entry[2])
        scenarioCaseType: str = entry[-1]
        if scenarioCaseType == "lowercase":
            CASE_SCENARIO_MAP[scenario] = toLowerCase
        elif scenarioCaseType == "uppercase":
            CASE_SCENARIO_MAP[scenario] = toUpperCase
        elif scenarioCaseType == "sentence":
            CASE_SCENARIO_MAP[scenario] = toSentenceCase

def refineCaseOfMapped(original: str, mapped: str) -> str:
    ogLength: str = "single" if len(original) == 1 else "multiple"
    mappedLength: str = "single" if len(mapped) == 1 else "multiple"
    ogCase: str = getCaseType(original)
    scenario: tuple[str, str, str] = (ogLength, mappedLength, ogCase)
    return CASE_SCENARIO_MAP[scenario](mapped)

def nestedDictContains3Layers(
    d: dict[int, dict[str, dict[str, str]]], length: int, lang: str, mapFrom: str
) -> bool:
    if length not in d:
        return False
    if lang not in d[length]:
        return False
    return mapFrom in d[length][lang]

def nestedDictContains2Layers(
    d: dict[int, dict[str, str]], length: int, mapFrom: str
) -> bool:
    if length not in d:
        return False
    return mapFrom in d[length]

def substituteAsterisk(rawMapped: str, index: int, content: str) -> str:
    if rawMapped != "v*":
        return rawMapped
    elif index == len(content) - 1:
        return "ł"
    elif toLowerCase(content[index + 1]) in VOWELS_LIST:
        return "v"
    else:
        return "ł"

def transliterateContent(content: str, language: Language) -> str:
    
    transliterated: str = ""
    index: int = 0

    while index < len(content):
        mapped: bool = False
        for length in range(MAX_MAPPING_LENGTH, 0, -1):

            substring: str = content[index : index + length]
            trueLength: int = len(substring)
            substringLower: str = toLowerCase(substring)
            
            if language.script == "cyrillic":
                if nestedDictContains3Layers(
                    CYRILLIC_SPECIFIC_MAP, trueLength, language.lang, substringLower
                ):
                    transliterated += refineCaseOfMapped(
                        substring, substituteAsterisk(
                            CYRILLIC_SPECIFIC_MAP[trueLength][language.lang][substringLower],
                            index, content
                        )
                    ); index += trueLength; mapped = True; break
                elif nestedDictContains2Layers(
                    CYRILLIC_DEFAULT_MAP, trueLength, substringLower
                ):
                    transliterated += refineCaseOfMapped(
                        substring, CYRILLIC_DEFAULT_MAP[trueLength][substringLower]
                    ); index += trueLength; mapped = True; break

            elif language.script == "latin":
                if nestedDictContains3Layers(
                    LATIN_SPECIFIC_MAP, trueLength, language.lang, substringLower
                ):
                    transliterated += refineCaseOfMapped(
                        substring, substituteAsterisk(
                            LATIN_SPECIFIC_MAP[trueLength][language.lang][substringLower],
                            index, content
                        )
                    ); index += trueLength; mapped = True; break
        
        if not mapped:
            transliterated += content[index]
            index += 1

    return transliterated

def transliterate(language: Language) -> None:
    
    inputFile: File = open(INPUT_FILE, "r", encoding = "utf-8")
    outputFile: File = open(OUTPUT_FILE, "w", encoding = "utf-8")

    content: str = inputFile.read()
    transliterated: str = transliterateContent(content, language)
    outputFile.write(transliterated)

    inputFile.close()
    outputFile.close()

if __name__ == "__main__":

    initializeUpperLowerMaps()
    initializeCyrillicDefaultMap()
    initializeSpecificMap(CYRILLIC_SPECIFIC_MAP, CYRILLIC_SPECIFIC_FILE)
    initializeSpecificMap(LATIN_SPECIFIC_MAP, LATIN_SPECIFIC_FILE)
    initializeChoiceToLangMap()
    initializeCaseScenarioMap()
    initializeVowelList()

    print("\nWelcome to the Common Slavic Alphabet transliterator!\n" +
          "Please select the language that you would like to transliterate:\n")
    
    for i in CHOICE_TO_LANGUAGE_MAP.keys():
        print(f"({i}) {CHOICE_TO_LANGUAGE_MAP[i].description}")

    try:
        choice: int = int(input("\nEnter your choice here: "))
        language: Language = CHOICE_TO_LANGUAGE_MAP[choice]
    except KeyError:
        print("Sorry, but you need to enter one of the choices shown above.")
        exit()
    except ValueError:
        print("Sorry, but you need to enter a valid integer.")
        exit()

    print(f"Your choice is {choice} and your language is \"{language.description}\".")
    transliterate(language)
    print(f"\nTransliteration complete!\nThank you for using this transliterator, and have a nice day!")