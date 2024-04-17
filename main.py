from io import TextIOWrapper as File

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

MAX_MAPPING_LENGTH: int = -1

CYRILLIC_DEFAULT_MAP: dict[int, dict[str, str]] = {}
CYRILLIC_SPECIFIC_MAP: dict[int, dict[str, dict[str, str]]] = {}
LATIN_SPECIFIC_MAP: dict[int, dict[str, dict[str, str]]] = {}
UPPER_TO_LOWER_MAP: dict[str, str] = {}
LOWER_TO_UPPER_MAP: dict[str, str] = {}
CHOICE_TO_LANGUAGE_MAP: dict[int, Language] = {}

def readFileAndSplitByLineAndSpace(filename: str) -> list[list[str]]:
    file: File = open(filename, "r", encoding = "utf-8")
    content: list[str] = file.read().split("\n")
    file.close()
    return [line.split(" ") for line in content]

def getMaxMappingLengthFromContent(content: list[list[str]]) -> int:
    global MAX_MAPPING_LENGTH
    lengths: list[int] = [len(entry[0]) for entry in content]
    maxLength: int = max(lengths)
    MAX_MAPPING_LENGTH = max(MAX_MAPPING_LENGTH, maxLength)
    return maxLength

def initializeDictToMaxLength(d: dict[int, dict[any, any]], maxLength: int) -> None:
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

if __name__ == "__main__":

    initializeUpperLowerMaps()
    initializeCyrillicDefaultMap()
    initializeSpecificMap(CYRILLIC_SPECIFIC_MAP, CYRILLIC_SPECIFIC_FILE)
    initializeSpecificMap(LATIN_SPECIFIC_MAP, LATIN_SPECIFIC_FILE)
    initializeChoiceToLangMap()

    print(readFileAndSplitByLineAndSpace(CYRILLIC_DEFAULT_FILE), end = "\n\n")
    print(CYRILLIC_DEFAULT_MAP, end = "\n\n")

    print(readFileAndSplitByLineAndSpace(CYRILLIC_SPECIFIC_FILE), end = "\n\n")
    print(CYRILLIC_SPECIFIC_MAP, end = "\n\n")

    print(readFileAndSplitByLineAndSpace(LATIN_SPECIFIC_FILE), end = "\n\n")
    print(LATIN_SPECIFIC_MAP, end = "\n\n")

    print(readFileAndSplitByLineAndSpace(UPPER_LOWER_FILE), end = "\n\n")
    print(UPPER_TO_LOWER_MAP, end = "\n\n")
    print(LOWER_TO_UPPER_MAP, end = "\n\n")

    print(readFileAndSplitByLineAndSpace(CHOICE_TO_LANGUAGE_FILE), end = "\n\n")
    print(CHOICE_TO_LANGUAGE_MAP, end = "\n\n")

    print(MAX_MAPPING_LENGTH)