"""
Language detection using n-grams
"""


import re
from math import log


# 4
def tokenize_by_sentence(text: str) -> tuple:
    """
    Splits a text into sentences, sentences into tokens, tokens into letters
    Tokens are framed with '_'
    :param text: a text
    :return: a tuple of sentence with tuples of tokens split into letters
    e.g.
    text = 'She is happy. He is happy.'
    -->  (
         (('_', 's', 'h', 'e', '_'), ('_', 'i', 's', '_'), ('_', 'h', 'a', 'p', 'p', 'y', '_')),
         (('_', 'h', 'e', '_'), ('_', 'i', 's', '_'), ('_', 'h', 'a', 'p', 'p', 'y', '_'))
         )
    """
    is_not_good_text = not(isinstance(text, str) and len(text))

    if is_not_good_text:
        return ()

    sentence_tokens = re.split('[?!.]', text)

    word_tokens = []
    for sentence in sentence_tokens:
        tokens = re.sub('[^a-z \n]', '', sentence.lower()).split()
        if not tokens:
            continue
        word_tokens.append(tuple([tuple(['_'] + list(token) + ['_']) for token in tokens]))

    return tuple(word_tokens)


def check_tuple(given_tuple: tuple) -> bool:
    return isinstance(given_tuple, tuple) and (not given_tuple or (given_tuple and given_tuple[0]))


# 4
class LetterStorage:

    def __init__(self):
        self.storage = {}

    def _put_letter(self, letter: str) -> int:
        """
        Puts a letter into storage, assigns a unique id
        :param letter: a letter
        :return: 0 if succeeds, 1 if not
        """
        is_not_good_letter = not(isinstance(letter, str) and len(letter) == 1)

        if is_not_good_letter:
            return 1

        if letter not in self.storage:
            self.storage[letter] = len(self.storage) + 1

        return 0

    def get_id_by_letter(self, letter: str) -> int:
        """
        Gets a unique id by a letter
        :param letter: a letter
        :return: an id
        """
        is_not_good_letter = not (isinstance(letter, str) and len(letter))

        if is_not_good_letter:
            return -1

        if letter in self.storage:
            return self.storage[letter]

        return -1

    def update(self, corpus: tuple) -> int:
        """
        Fills a storage by letters from the corpus
        :param corpus: a tuple of sentences
        :return: 0 if succeeds, 1 if not
        """

        if not isinstance(corpus, tuple):
            return 1

        for sentence in corpus:
            for word in sentence:
                for element in word:
                    self._put_letter(element)

        return 0


# 6
def encode_corpus(storage: LetterStorage, corpus: tuple) -> tuple:
    """
    Encodes sentences by replacing letters with their ids
    :param storage: an instance of the LetterStorage class
    :param corpus: a tuple of sentences
    :return: a tuple of the encoded sentences
    """
    is_not_good_storage = not isinstance(storage, LetterStorage)
    is_not_good_corpus = not(isinstance(corpus, tuple) and len(corpus))

    if is_not_good_storage or is_not_good_corpus:
        return ()

    encoded_corpus = []
    for sentence in corpus:
        encoded_sentence = []
        if isinstance(sentence[0], tuple):
            for word in sentence:
                encoded_sentence.append(tuple(storage.get_id_by_letter(letter) for letter in word))
        else:
            encoded_sentence.append(tuple(storage.get_id_by_letter(letter) for letter in sentence))

        encoded_corpus.append(tuple(encoded_sentence))

    return tuple(encoded_corpus)


# 6
class NGramTrie:

    def __init__(self, n: int):
        self.size = n
        self.n_grams = ()
        self.n_gram_frequencies = {}
        self.n_gram_log_probabilities = {}

    def fill_n_grams(self, encoded_text: tuple) -> int:
        """
        Extracts n-grams from the given sentence, fills the field n_grams
        :return: 0 if succeeds, 1 if not
        """

        if not isinstance(encoded_text, tuple):
            return 1

        self.n_grams = []
        for sentence in encoded_text:
            sentence_grams = []
            for word in sentence:
                word_grams = []
                for ind_letter in range(len(word[:-self.size + 1])):
                    word_grams.append(tuple(word[ind_letter:ind_letter + self.size]))

                sentence_grams.append(tuple(word_grams))

            self.n_grams.append(tuple(sentence_grams))

        self.n_grams = tuple(self.n_grams)
        return 0

    def calculate_n_grams_frequencies(self) -> int:
        """
        Fills in the n-gram storage from a sentence, fills the field n_gram_frequencies
        :return: 0 if succeeds, 1 if not
        """
        for sentence in self.n_grams:
            for word in sentence:
                for gram in word:
                    self.n_gram_frequencies[gram] = self.n_gram_frequencies.get(gram, 0) + 1

        if self.n_gram_frequencies:
            return 0
        return 1

    def calculate_log_probabilities(self) -> int:
        """
        Gets log-probabilities of n-grams, fills the field n_gram_log_probabilities
        :return: 0 if succeeds, 1 if not
        """

        if not self.n_gram_frequencies:
            return 1

        prob_dict = {}

        for gram in self.n_gram_frequencies:
            probability = self.n_gram_frequencies[gram] / sum([self.n_gram_frequencies[another_gram] for another_gram in
                                                    self.n_gram_frequencies if another_gram[0] == gram[0]])
            prob_dict[gram] = log(probability)

        self.n_gram_log_probabilities = prob_dict

        return 0

    def top_n_grams(self, k: int) -> tuple:
        """
        Gets k most common n-grams
        :return: a tuple with k most common n-grams
        """
        if not isinstance(k, int) or k < 1:
            return ()

        freq_dict = {}
        for key, value in self.n_gram_frequencies.items():
            freq_dict[value] = freq_dict.get(value, ()) + key

        sorted_freq = sorted(list(freq_dict.keys()), reverse=True)
        top_grams = []
        for i in range(min(k, len(sorted_freq))):
            top_grams.append(freq_dict[sorted_freq[i]])

        return tuple(top_grams)


# 8
class LanguageDetector:

    def __init__(self, trie_levels: tuple = (2,), top_k: int = 10):
        self.trie_levels = trie_levels
        self.top_k = top_k
        self.n_gram_storages = {}

    def new_language(self, encoded_text: tuple, language_name: str) -> int:
        """
        Fills NGramTries with regard to the trie_levels field
        :param encoded_text: an encoded text
        :param language_name: a language
        :return: 0 if succeeds, 1 if not
        """
        is_not_good_encoded_text = not(isinstance(encoded_text, tuple) and len(encoded_text) and encoded_text[0])
        if is_not_good_encoded_text or not isinstance(language_name, str):
            return 1

        self.n_gram_storages[language_name] = {n: NGramTrie(n) for n in self.trie_levels}

        for level in self.trie_levels:
            self.n_gram_storages[language_name][level].fill_n_grams(encoded_text)

        return 0

    @staticmethod
    def _calculate_distance(first_n_grams: tuple, second_n_grams: tuple) -> int:
        """
        Calculates distance between top_k n-grams
        :param first_n_grams: a tuple of the top_k n-grams
        :param second_n_grams: a tuple of the top_k n-grams
        :return: a distance
        """

        if not check_tuple(first_n_grams) or not check_tuple(second_n_grams):
            return -1

        if not first_n_grams or not second_n_grams:
            return 0

        distance = []
        second_length = len(second_n_grams)

        for n_gram1 in set(first_n_grams):
            if n_gram1 in second_n_grams:
                distance.append(abs(first_n_grams.index(n_gram1) - second_n_grams.index(n_gram1)))
            else:
                distance.append(second_length)

        distance_sum = sum(distance)

        return distance_sum

    def detect_language(self, encoded_text: tuple) -> dict:
        """
        Detects the language the unknown text is written in using the function _calculate_distance
        :param encoded_text: a tuple of sentences with tuples of tokens split into letters
        :return: a dictionary where a key is a language, a value ??? the distance
        """
        is_not_good_encoded_text = not(isinstance(encoded_text, tuple) and len(encoded_text) and encoded_text[0])

        if is_not_good_encoded_text or not self.n_gram_storages:
            return {}

        levels = self.n_gram_storages['english'].keys()

        encoded_text_dict = {}
        for level in levels:
            i_ngramtrie = NGramTrie(level)
            i_ngramtrie.fill_n_grams(encoded_text)
            i_ngramtrie.calculate_n_grams_frequencies()
            top_text = i_ngramtrie.top_n_grams(self.top_k)

            encoded_text_dict[level] = top_text

        distance_dict = {}
        for language in self.n_gram_storages:
            sum_list = []
            for level in levels:
                self.n_gram_storages[language][level].calculate_n_grams_frequencies()
                language_top_grams = self.n_gram_storages[language][level].top_n_grams(self.top_k)

                sum_list.append(self._calculate_distance(encoded_text_dict[level], language_top_grams))

            distance_dict[language] = sum(sum_list) / len(sum_list)

        return distance_dict


# 10
class ProbabilityLanguageDetector(LanguageDetector):

    @staticmethod
    def _calculate_sentence_probability(n_gram_storage: NGramTrie, sentence_n_grams: tuple) -> float:
        """
        Calculates sentence probability
        :param n_gram_storage: a filled NGramTrie with log-probabilities
        :param sentence_n_grams: n-grams from a sentence
        :return: a probability of a sentence
        """
        if not isinstance(n_gram_storage, NGramTrie) or not isinstance(sentence_n_grams, tuple):
            return -1.0

        probability_sum = 0
        n_gram_storage.calculate_n_grams_frequencies()
        n_gram_storage.calculate_log_probabilities()

        for sentence in sentence_n_grams:
            for word in sentence:
                for gram in word:
                    probability_sum += n_gram_storage.n_gram_log_probabilities.get(gram, 0)

        return probability_sum

    def detect_language(self, encoded_text: tuple) -> dict:
        """
        Detects the language the unknown sentence is written in using sentence probability in different languages
        :param encoded_text: a tuple of sentences with tuples of tokens split into letters
        :return: a dictionary with language_name: probability
        """
        if not isinstance(encoded_text, tuple):
            return {}

        probability_dict = {}
        for language in self.n_gram_storages:
            probability_dict[language] = [self._calculate_sentence_probability(level, encoded_text)
                                          for level in self.n_gram_storages[language].values()]
            probability_dict[language] = sum(probability_dict[language]) / len(probability_dict[language])

        return probability_dict
