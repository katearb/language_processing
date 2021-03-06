"""
Concordance implementation starter
"""

import os
import main


if __name__ == '__main__':
    #  use data.txt file to test your program
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data = main.read_from_file(os.path.join(current_dir, 'data.txt'))
    stop_words = main.read_from_file(os.path.join(current_dir, 'stop_words.txt')).split('\n')

    #  here goes your logic: calling methods from concordance.py
    tokens = main.tokenize(data)
    print('tokens:', tokens[:10])
    print('\n-----------------------------\n')

    tokens = main.remove_stop_words(tokens, stop_words)   # old: 34 sec, new - 3.4 sec
    print('tokens without stop words:', tokens[:10])
    print('\n-----------------------------\n')

    frequencies = main.calculate_frequencies(tokens)  # old: 116 sec, new: ~81 sec
    print('frequency for the first word:', frequencies[tokens[0]])
    print('\n-----------------------------\n')

    top_10 = main.get_top_n_words(frequencies, 10)
    print('top 10 words:', top_10)
    print('\n-----------------------------\n')

    concordance_cat = main.get_concordance(tokens, 'cat', 2, 3)
    print('concordance for "cat", left = 2, right = 3:', concordance_cat[:5])
    print('\n-----------------------------\n')

    adjacent_words_cat = main.get_adjacent_words(tokens, 'cat', 2, 3)
    print('adjacent words for "cat" left = 2, right = 3:', adjacent_words_cat[:5])
    print('\n-----------------------------\n')

    sorted_concordance_cat = main.sort_concordance(tokens, 'cat', 2, 3, True)
    print('sorted concordance for "cat" left = 2, right = 3:', sorted_concordance_cat[:5])
    print('\n-----------------------------\n')

    #  main.write_to_file('report.txt', sorted_concordance_cat)

    RESULT = sorted_concordance_cat

    tokenized_data = main.tokenize(data)
    clean_data = main.remove_stop_words(tokenized_data, stop_words)

    top_n = main.get_top_n_words(main.calculate_frequencies(clean_data), 13)
    key_word = top_n[-1]
    print(f'13th popular word: {key_word}. Let`s use if for further functions')

    closest_words = main.get_adjacent_words(clean_data, key_word, 3, 2)
    if len(closest_words) > 0:
        print(f"\nThird words from the left and second words from the right for "
              f"the word '{key_word}' (first 5 cases) are")
        for adjacent_words in closest_words[:5]:
            print('\t', adjacent_words)

    concordances = main.get_concordance(clean_data, key_word, 2, 2)
    if len(concordances) > 0:
        print(f"\nThe first three concordances (with 2 word on the left and 2 on the right)"
              f"for the word '{key_word}' are")
        for context in concordances[:3]:
            print('\t', context)

    sorted_concordance_left = main.sort_concordance(clean_data, key_word, 2, 2, True)
    if len(sorted_concordance_left) > 0:
        print('\nConcordance sorted by the first left word (first 5 cases):')
        for concordance in sorted_concordance_left[:5]:
            print('\t', concordance)

    sorted_concordance_right = main.sort_concordance(clean_data, key_word, 2, 2, False)
    if len(sorted_concordance_right) > 0:
        print('\nConcordance sorted by the first right word (first 5 cases):')
        for concordance in sorted_concordance_right[:5]:
            print('\t', concordance)

    RESULT = sorted_concordance_left
    # DO NOT REMOVE NEXT LINE - KEEP IT INTENTIONALLY LAST
    assert RESULT, 'Concordance not working'
