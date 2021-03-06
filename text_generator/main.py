"""
Lab 4
"""

import re
import random
import json
from ngrams.ngram_trie import NGramTrie


def tokenize_by_sentence(text: str) -> tuple:
    if not isinstance(text, str):
        raise ValueError

    text_clean = re.sub(r'[^A-Za-z !?.]', '', text).lower()

    if not text_clean:
        return ()

    prepared_text = re.sub(r'[!?.$]', ' <END> ', text_clean)
    tokenized_text = prepared_text.split()

    if tokenized_text[-1] != '<END>':
        tokenized_text.append('<END>')

    return tuple(tokenized_text)


class WordStorage:
    def __init__(self):
        self.storage = {}

    def _put_word(self, word: str):
        if not isinstance(word, str) or not word:
            raise ValueError

        try:
            self.storage[word]
        except KeyError:
            self.storage[word] = len(self.storage) + 1

        return self.storage[word]

    def get_id(self, word: str) -> int:
        if not isinstance(word, str):
            raise ValueError

        if word not in self.storage:
            raise KeyError

        return self.storage[word]

    def get_word(self, word_id: int) -> str:
        if isinstance(word_id, bool) or not isinstance(word_id, int) or word_id < 0:
            raise ValueError

        if word_id not in self.storage.values():
            raise KeyError

        inverted_storage = {v: k for k, v in self.storage.items()}

        return inverted_storage[word_id]

    def update(self, corpus: tuple):
        if not isinstance(corpus, tuple):
            raise ValueError

        for word in corpus:
            self._put_word(word)


def encode_text(storage: WordStorage, text: tuple) -> tuple:
    if not isinstance(storage, WordStorage) or not isinstance(text, tuple):
        raise ValueError

    encoded_text = [storage.get_id(word) for word in text]

    return tuple(encoded_text)


class NGramTextGenerator:
    def __init__(self, word_storage: WordStorage, n_gram_trie: NGramTrie):
        self._word_storage = word_storage
        self._n_gram_trie = n_gram_trie

    def _generate_next_word(self, context: tuple) -> int:
        if not isinstance(context, tuple) or len(context) + 1 != self._n_gram_trie.size:
            raise ValueError

        most_frequent_word = ''
        word_frequency = 0

        for n_gram, n_gram_frequency in self._n_gram_trie.n_gram_frequencies.items():
            if n_gram[:-1] == context and n_gram_frequency > word_frequency:
                most_frequent_word = n_gram[-1]
                word_frequency = n_gram_frequency

        if not most_frequent_word:
            most_frequent_word = max(self._n_gram_trie.uni_grams, key=self._n_gram_trie.uni_grams.get)[0]

        return most_frequent_word

    def _generate_sentence(self, context: tuple) -> tuple:
        if not isinstance(context, tuple) or len(context) + 1 != self._n_gram_trie.size:
            raise ValueError

        end_code = self._word_storage.get_id('<END>')

        if context[-1] == end_code:
            sentence = []
        else:
            sentence = list(context)

        context_len = len(context)
        count = 0
        while count != 20:
            sentence.append(self._generate_next_word(context))
            context = tuple(list(context) + sentence)[-context_len:]
            count += 1

            if sentence[-1] == end_code:
                if len(sentence) == 1:
                    uni_grams_no_end = list(self._n_gram_trie.uni_grams.keys())
                    uni_grams_no_end.remove((end_code,))
                    sentence = random.choices(uni_grams_no_end, k=5) + [(end_code,)]
                    return tuple(word_id[0] for word_id in sentence)

                return sentence

        sentence.append(end_code)
        return tuple(sentence)

    def generate_text(self, context: tuple, number_of_sentences: int) -> tuple:
        if not isinstance(context, tuple) or not isinstance(number_of_sentences, int) \
                or (len(context) + 1) != self._n_gram_trie.size:
            raise ValueError

        context_len = len(context)
        text = []

        for _ in range(number_of_sentences):
            new_sentence = self._generate_sentence(context)

            text.extend(new_sentence)
            context = tuple(text[-context_len:])

        return tuple(text)

    @property
    def word_storage(self):
        return self._word_storage

    @property
    def n_gram_trie(self):
        return self._n_gram_trie


class LikelihoodBasedTextGenerator(NGramTextGenerator):

    def _calculate_maximum_likelihood(self, word: int, context: tuple) -> float:
        if not isinstance(word, int) or not isinstance(context, tuple) or (word,) not in self._n_gram_trie.uni_grams \
                or len(context) + 1 != self._n_gram_trie.size:
            raise ValueError

        context_len = len(context)
        context_frequency = sum([n_gram_freq for n_gram, n_gram_freq in self._n_gram_trie.n_gram_frequencies.items()
                                 if n_gram[:context_len] == context])

        context_word = context + (word,)
        context_word_frequency = self._n_gram_trie.n_gram_frequencies.get(context_word, 0.0)

        if context_frequency:
            return context_word_frequency / context_frequency

        return context_word_frequency

    def _generate_next_word(self, context: tuple) -> int:
        if not isinstance(context, tuple) or len(context) + 1 != self._n_gram_trie.size or \
                context[0] > len(self._word_storage.storage):
            raise ValueError

        next_word = 0
        next_word_frequency = 0.0

        for word in self._word_storage.storage.values():
            word_frequency = self._calculate_maximum_likelihood(word, context)
            if word_frequency > next_word_frequency:
                next_word = word
                next_word_frequency = word_frequency

        if not next_word:
            next_word = max(self._n_gram_trie.uni_grams, key=self._n_gram_trie.uni_grams.get)[0]

        return next_word


def _generate_next_word_different_level(context, n_gram_tries):
    most_frequent_word = ''
    word_frequency = 0

    for n_gram_trie in n_gram_tries:
        for n_gram, n_gram_frequency in n_gram_trie.n_gram_frequencies.items():
            if n_gram[:-1] == context and n_gram_frequency > word_frequency:
                most_frequent_word = n_gram[-1]
                word_frequency = n_gram_frequency

        if most_frequent_word:
            return most_frequent_word

    return most_frequent_word


class BackOffGenerator(NGramTextGenerator):

    def __init__(self, word_storage: WordStorage, n_gram_trie: NGramTrie, *args):
        super().__init__(word_storage, n_gram_trie)
        self._n_gram_tries = (n_gram_trie,) + args

    def _generate_next_word(self, context: tuple) -> int:
        if not isinstance(context, tuple) or not context:
            raise ValueError

        context_correct = all(word in self._word_storage.storage.values() for word in context)
        if not context_correct:
            raise ValueError

        most_frequent_word = _generate_next_word_different_level(context, self._n_gram_tries)

        if not most_frequent_word:
            most_frequent_word = max(self._n_gram_trie.uni_grams, key=self._n_gram_trie.uni_grams.get)[0]

        return most_frequent_word


def decode_text(storage: WordStorage, encoded_text: tuple) -> tuple:
    if not isinstance(storage, WordStorage) or not isinstance(encoded_text, tuple) or not encoded_text:
        raise ValueError

    decoded_text = []
    decoded_sentence = []
    for word_id in encoded_text:
        decoded_word = storage.get_word(word_id)
        if decoded_word.lower() == '<end>':
            decoded_text.append(' '.join(decoded_sentence))
            decoded_sentence = []
            continue

        if not decoded_sentence:
            decoded_sentence.append(decoded_word.capitalize())
        else:
            decoded_sentence.append(decoded_word)

    return tuple(decoded_text)


def save_model(model: NGramTextGenerator, path_to_saved_model: str):
    if not isinstance(model, NGramTextGenerator) or not isinstance(path_to_saved_model, str):
        raise ValueError

    str_frequencies = {', '.join(map(str, key)): value for key, value in model.n_gram_trie.n_gram_frequencies.items()}
    str_unigrams = {key[0]: value for key, value in model.n_gram_trie.uni_grams.items()}
    model_to_save = {'word_storage': model.word_storage.storage,
                     'n_grams': model.n_gram_trie.n_grams,
                     'n_gram_trie_size': model.n_gram_trie.size,
                     'n_gram_trie_frequencies': str_frequencies,
                     'uni_grams': str_unigrams}

    try:
        with open(path_to_saved_model, 'w') as file:
            file.write(json.dumps(model_to_save))

    except FileNotFoundError:
        raise FileNotFoundError


def load_model(path_to_saved_model: str) -> NGramTextGenerator:
    if not isinstance(path_to_saved_model, str):
        raise ValueError

    try:
        with open(path_to_saved_model, 'r') as file:
            model = json.load(file)

        word_storage = WordStorage()
        word_storage.storage = model['word_storage']

        trie = NGramTrie(n_gram_size=int(model['n_gram_trie_size']),
                         encoded_text=('he',) * int(model['n_gram_trie_size']))
        trie.n_grams = tuple([tuple(n_gram) for n_gram in model['n_grams']])
        trie.n_gram_frequencies = {tuple(map(int, key.split(', '))): value for key, value
                                   in model['n_gram_trie_frequencies'].items()}
        trie.uni_grams = {(int(key),): value for key, value in model['uni_grams'].items()}

        model_generator = NGramTextGenerator(word_storage, trie)

        return model_generator
    except FileNotFoundError:
        raise FileNotFoundError
