import json
import string
import operator


def make_frequencies(s):
    distribution = {}
    st = "".join(c for c in s.lower() if c in string.ascii_lowercase)
    length = len(st)
    for char in st:
        distribution[char] = distribution.get(char, 0) + 1
    for char, frequency in distribution.items():
        distribution[char] = frequency / length
    return distribution


def get_words(s):
    frequencies = {}
    valid = string.ascii_lowercase + " "
    for word in "".join(c for c in s.lower() if c in valid).split():
        frequencies[word] = frequencies.get(word, 0) + 1
    return [x[0] for x in sorted(frequencies.items(), key=lambda kv: kv[1], reverse=True)]


def solve(s):
    s = s.lower()
    distribution = make_frequencies(s)
    mapping = {}
    rmapping = {}
    mapping[try_letter(s, distribution, "e")] = "e"
    rmapping["e"] = try_letter(s, distribution, "e")
    words = get_words(s)
    get_word(words, mapping, "the")
    while get_any_word(words, mapping):
        pass
#    get_any_word(words, mapping)
    print(mapping)
    print(s.translate(str.maketrans(mapping)))


def get_word(words, mapping, word):
    orig = word
    length = len(word)
    target = abstractify_word(word)
    for word in words:
        if len(word) == length and abstractify_word(word) == target:
            i = 0
            okay = True
            found = 0
            for char in orig:
                if char in mapping.keys():
                    if mapping[char] != word[i]:
                        okay = False
                        break
                    found += 1
                i += 1
            if not okay:
                continue
            # This is the word! add it to mapping
            i = 0
            for char in orig:
                mapping[word[i]] = char
                i += 1
            break


def get_any_word(words, mapping):
    for word in words:
        try:
            found_words = WORDS[abstractify_word(word)]
        except KeyError:
            continue  # Word not in dictionary
        matching_words = {}
        for found_word in found_words:
            i = 0
            okay = True
            matched = 0
            for char in found_word:
                if word[i] in mapping:
                    if mapping[word[i]] == char:
                        matched += 1
                    else:
                        okay = False
                        break
                i += 1
            if not okay:
                continue  # it might be the next one
#            if matched + 2 < len(word):
#                print(f"too short {matched} {len(word)}")
#                continue
            matching_words[found_word] = matched  # Okay, it's the word (hopefully)
        if not matching_words:
            continue  # No words match
        last_confidence = 0
        conflict = False
        for match, confidence in sorted(matching_words.items(), key=lambda kv: kv[1], reverse=True):
            if confidence == last_confidence:
                conflict = True
                break
            last_confidence = confidence
        if conflict:
            continue
        # There's only one word which matches this well, let's go!
        i = 0
        changed = False
        for char in match:
            if word[i] not in mapping:
                mapping[word[i]] = char
                changed = True
            assert mapping[word[i]] == char
            i += 1
        if changed:
            print(f"Solved {word} as {match}")
            return True
        else:
            continue
    print("Failed to solve more")
    return False


def abstractify_word(word):
    abstract_mapping = {}
    max_id = 0
    ret = []
    for char in word:
        if char not in abstract_mapping.keys():
            abstract_mapping[char] = max_id
            max_id += 1
        ret.append(abstract_mapping[char])
    return tuple(ret)


def try_letters(s):
    distribution = make_frequencies(s)
    changed = True
    mapping = {}
    for letter in FREQUENCIES.keys():
        repl = try_letter(s, distribution, letter)
        assert repl not in mapping.keys()
        if repl is None:
            pass  # Only ever happens if the target letter is not present in the text
        else:
            mapping[repl] = letter
    print(mapping)
    ret = s.lower().translate(str.maketrans(mapping))
    print(ret)


def try_letter(s, frequencies, letter):
    i = 0
    for char, frequency in FREQUENCIES.items():
        if char == letter:
            break
        i += 1
    try:
        return list(dict(sorted(frequencies.items(), key=lambda kv: kv[1], reverse=True)).items())[i][0]
    except IndexError:
        return None

def count_alphabets(s):
    ALPHABET_ENGLISH = 1.73
    ALPHABET_OFFSET = 0.05
    MAX_ALPHABETS = 15
    for alphabets in range(1, MAX_ALPHABETS):
        total_ioc = 0
        for offset in range(alphabets):
            ioc = calculate_ioc(s[offset::alphabets])
            total_ioc += ioc
#        print(alphabets, total_ioc / alphabets)
        if total_ioc / alphabets > ALPHABET_ENGLISH - ALPHABET_OFFSET and total_ioc / alphabets < ALPHABET_ENGLISH + ALPHABET_OFFSET:
            return alphabets
    return None


def calculate_ioc(s, normalise=26):
    ret = 0
    st = "".join(c for c in s.lower() if c in string.ascii_lowercase)  # go lowercase and remove all non-letters
    length = len(st)
    if length <= 1:
        return 0
    for char in string.ascii_lowercase:
        if char in st:
            ret += (st.count(char) / length) * ((st.count(char) - 1) / (length - 1))
    return normalise * ret


FREQUENCIES = dict(sorted(json.load(open("frequencies.json")).items(), key=lambda kv: kv[1], reverse=True))
WORDS = {}
for word in open("english-words/words_alpha.txt").readlines():
    WORDS.setdefault(abstractify_word(word.lower().strip()), []).append(word.lower().strip())
#WORDS = {word.lower().strip(): abstractify_word(word.lower().strip()) for word in open("english-words/words_alpha.txt").readlines()}


def main():
    s = ""
    t = True
    while t != "":
        t = input("Enter the ciphertext, and a blank line to finish: ")
        s += t + "\n"
    print()
    print()
    print()
    alphabets = count_alphabets(s)
    print("alphabets\t\t", alphabets)
    for alphabet in range(alphabets):
        subtext = s[alphabet::alphabets]  # TODO: this won't work for multiple alphabets, because it includes special chars
        solve(subtext)

if __name__ == "__main__":
    main()
