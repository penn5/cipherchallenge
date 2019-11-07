import json
import string
import operator
import itertools
import collections
import copy
import math



ALPHABET_ENGLISH = 1.73
ALPHABET_OFFSET = 0.15
MAX_ALPHABETS = 30
TRANS_THE_RATIO = 100
TRANS_WORD_RATIO = 0.37


def cleanup_str(s, spaces=True):
    return "".join(c if c in (string.ascii_lowercase + (" " if spaces else "")) else (" " if spaces else "") for c in s.lower())


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
    for word in cleanup_str(s).split():
        frequencies[word] = frequencies.get(word, 0) + 1
    return [x[0] for x in sorted(frequencies.items(), key=lambda kv: kv[1], reverse=True)]


def solve(ost, alphabets=1, given_mapping=None):
    st = cleanup_str(ost, False)
    maps = []
    for alphabet in range(alphabets):
        s = st[alphabet::alphabets]
        distribution = make_frequencies(s)
        print(distribution)
        if given_mapping is None:
            mapping = {}
        else:
            mapping = given_mapping[alphabet]
        mapping[try_letter(s, distribution, "e")] = "e"
        mapping[try_letter(s, distribution, "t")] = "t"
        if set(("e", "t")) == mapping.keys():
            print("Transposition cipher detected.")
#            print(trans_perm_guess(s))
            print(trans_col_guess(s))
            return
        print(mapping)
        print(s.translate(str.maketrans(mapping)))
        maps.append(mapping)
    # Find "the"
#    for start in range(len(s) - 3):
#        sub = s[start:start + 3]
#        base_alphabet = start % alphabets
#        if len(set(sub)) != 3:
#            continue
#        if maps[base_alphabet][sub[0]] == "t" and maps[(base_alphabet + 2) % alphabets][sub[2]] == "e":
#            # Probably says "the"
#            maps[(base_alphabet + 1) % alphabets][sub[1]] = "h"
#    # Find "that"
#    for start in range(len(s) - 4):
#        sub = s[start:start + 4]
#        base_alphabet = start % alphabets
#        if len(set(sub)) != 3:
#            continue
#        if maps[base_alphabet][sub[0]] == "t" and maps[(base_alphabet + 1) % alphabets][sub[1]] == "h" \
#                and maps[(base_alphabet) + :
#            # Probably says "the"
#            maps[(base_alphabet + 1) % alphabets][sub[1]] = "h"
    modified = True
    lastmaps = copy.deepcopy(maps)
    while modified:
        check_word(s, "the", maps, alphabets)
        print(maps)
        check_word(s, "that", maps, alphabets)
        print(maps)
        there = check_word(s, "there", maps, alphabets)
        print(maps)
        check_word(s, "what", maps, alphabets)
        print(maps)
        check_word(s, "when", maps, alphabets)
        print(maps)
        check_word(s, "which", maps, alphabets)
        print(maps)
        check_word(s, "who", maps, alphabets)
        print(maps)
        check_word(s, "and", maps, alphabets, 1)
        print(maps)
        check_word(s, "have", maps, alphabets)
        print(maps)
        check_word(s, "from", maps, alphabets)
        print(maps)
        check_word(s, "ight", maps, alphabets)
        print(maps)
        check_word(s, "less", maps, alphabets)
        print(maps)
        check_word(s, "our", maps, alphabets)
        print(maps)
        check_word(s, "this", maps, alphabets)
        print(maps)
        check_word(s, "are", maps, alphabets)
        print(maps)
        if lastmaps == maps:
            modified = False
        else:
            lastmaps = copy.deepcopy(maps)

    while True:


#    for i in range(alphabets):
#        ret.append(s[i::alphabets].translate(str.maketrans(maps[i])))
        alphabet = 0
        ret = []
        for i in range(len(s)):
            if s[i] in maps[alphabet]:
                ret.append("\u001b[32;1m" + maps[alphabet][s[i]] + "\033[0m")
            else:
                ret.append("\u001b[31;1m" + s[i] + "\033[0m")
            alphabet = alphabet + 1 % alphabets

        print("".join(ret))


        inp = input("Please enter a mapping: ").lower().strip()
        if not len(inp):
            print("Aborted")
            break
        if len(inp) not in (3, 4):
            print("Wrong count")
            continue
        if len(inp) == 4 and inp[3] != "=":
            print("Wrong count")
            continue
        if len(inp) == 4:
            override = True
        else:
            override = False
        if inp[1] not in string.ascii_lowercase or inp[2] not in string.ascii_lowercase:
            print("Invalid format")
            continue
        try:
            alphabet = int(inp[0])
        except ValueError:
            print("Invalid alphabet")
            continue
        if inp[2] in maps[alphabet].values():
            if override:
                maps[alphabet] = {k: v for k, v in maps[alphabet].items() if v != inp[2]}
                print("Dest overriden")
            else:
                print("Dest already used. Override by putting a '+' at the end.")
                continue
        maps[alphabet][inp[1]] = inp[2]
        print(maps)
    ret = ""
    i = 0
    for char in ost:
        if char in string.ascii_lowercase and char in maps[i % alphabets]:
            ret += maps[i % alphabets][char]
        else:
            ret += char
        i += 1
    print(ret)
    return mapping


def trans_perm_gen(s):
    for length in range(3, 7):
        for permu in itertools.permutations(range(length)):
            tmp = []
            for start in range(0, len(s), length):
                if start + length > len(s):
                    tmp.append(s[start:])
                else:
                    tmp.append("".join(s[start + x] for x in permu))
            yield permu, "".join(tmp)


def trans_perm_guess(s):
    for permu, poss in trans_perm_gen(s):
        the_count = poss.count("the")
        if the_count and len(s) / the_count < TRANS_THE_RATIO:
            return poss
        print(permu)
        for col in trans_col_gen(poss):
            the_count = col.count("the")
            print(the_count)
            if the_count and len(s) / the_count < TRANS_THE_RATIO:
                return poss

def trans_col_gen(s):
    slen = len(s)
    for rowlen in range(15, 2, -1):
        collen = slen / rowlen
        if not collen.is_integer():
            continue
        collen = int(collen)
        for permu in itertools.permutations(range(rowlen)):
            poss = "".join(s[offset::collen] for offset in range(collen))
            permutated = "".join(poss[c + i] for c in range(0, slen, rowlen) for i in permu)
            print(permu)
            yield permu, permutated


def trans_col_guess(s):
    for permu, poss in trans_col_gen(s):
#        the_count = poss.count("the")
        word_ratio = get_word_ratio(poss[:100])
        if word_ratio > TRANS_WORD_RATIO:
            return poss
#        if the_count and len(s) / the_count < TRANS_THE_RATIO:
#            return poss


def get_word_ratio(s):
    slen = len(s)
    found = 0
    offset = 0
    while offset < slen:
        for wordlen in range(min(7, slen - offset), 2, -1):
            if s[offset:offset + wordlen] in ALLWORDS:
                found += wordlen
                offset += wordlen
                break
        offset += 1
    print("word ratio", found / slen)
    return found / slen


def check_word(s, target, maps, alphabets, thresh=None):
    uniqlen = len(set(target))
    l = len(target)
    matches = []
    if thresh is None:
        thresh = l - 1
    for start in range(len(s) - l):
        sub = s[start:start + l]
        base_alphabet = start % alphabets
        matched = 0
        for i in range(l):
            if sub[i] not in maps[base_alphabet + i % alphabets]:
                if target[i] in maps[base_alphabet + i % alphabets].values():
                    # The value we want is set, but its key isn't the one we are on. Clearly, something is wrong.
                    matched = 0
                    break
                continue  # Not set in mapping
            if maps[base_alphabet + i % alphabets][sub[i]] != target[i]:
                matched = 0  # It's wrong.
                break
            matched += 1
        if matched < thresh:
            continue
        matches.append(sub)

    if not matches:
        print(f"Could not match {target}!")
        return []

    print(matches)

    counter = collections.Counter(matches)

    common = counter.most_common(2)
    if len(common) > 1 and common[0][1] == common[1][1]:
        print(f"Equal split while matching {target} ({common})")
        ret = []
        lastfreq = None
        for word, freq in counter.most_common():
           if freq != lastfreq and lastfreq is not None:
               return ret
           ret.append(word)
           lastfreq = freq
        return ret
    sub = common[0][0]
    for i in range(l):
        if sub[i] in maps[base_alphabet + i % alphabets]:
            assert maps[base_alphabet + i % alphabets][sub[i]] == target[i], (sub, target, i, maps, base_alphabet, alphabets)
        maps[base_alphabet + i % alphabets][sub[i]] = target[i]
    print(f"Matched {target} to {sub}")
    return [sub]


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


def try_letters(s, mapping, distribution):
    for letter in FREQUENCIES.keys():
        repl = try_letter(s, distribution, letter)
        assert repl not in mapping.keys() or mapping[repl] == letter, (letter, mapping.items(), repl)
        if repl is None:
            pass  # Only ever happens if the target letter is not present in the text
        else:
            mapping[repl] = letter


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
    for alphabets in range(1, MAX_ALPHABETS):
        total_ioc = 0
        for offset in range(alphabets):
            ioc = calculate_ioc(s[offset::alphabets])
            total_ioc += ioc
        print(total_ioc / alphabets)
        if total_ioc / alphabets > ALPHABET_ENGLISH - ALPHABET_OFFSET and total_ioc / alphabets < ALPHABET_ENGLISH + ALPHABET_OFFSET:
            return alphabets
    return None


def calculate_ioc(s, normalise=26):
    ret = 0
    st = cleanup_str(s, False)
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
ALLWORDS = []
for word in open("The-Oxford-3000/The_Oxford_3000.txt").readlines():
    if len(word.strip()) in range(2, 7):
        ALLWORDS.append(word.lower().strip())


def main():
    s = ""
    t = ""
    while t != "EOF":
        s += t + "\n"
        t = input("Enter the ciphertext, and 'EOF' to finish: ")
    print()
    print()
    print()
    alphabets = count_alphabets(s)
    print("alphabets\t\t", alphabets)
    subtext = cleanup_str(s)
    alphabet = solve(subtext, alphabets)
    for letter in string.ascii_lowercase:
        if letter in s.lower() and letter not in alphabet.keys():
            print(f"Failed to solve {letter} from ciphertext")
        if letter not in alphabet.values():
            print(f"Failed to solve {letter} from plaintext")
    for letter in string.ascii_lowercase:
        if letter in s.lower() and letter not in alphabet.keys():
            value = input(f"Please enter the value for letter {letter} from ciphertext: ")
            if len(value) != 1:
                print("Skipped.")

if __name__ == "__main__":
    main()
