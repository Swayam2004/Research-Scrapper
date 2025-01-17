from math import log
from collections import defaultdict
import string
import asyncio

def update_name_scores(old: dict[str, float], new: dict[str, float]):
    for name, score in new.items():
        if name in old:
            old[name] += score
        else:
            old[name] = score
    
    return old


def normalize_string(input_string: str) -> str:
    translation_table = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
    string_without_punc = input_string.translate(translation_table)
    string_without_double_spaces = ' '.join(string_without_punc.split())
    return string_without_double_spaces.lower()

class SearchEngine:
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self._index: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self._documents: dict[str, str] = {}
        self._avdl: float | None = None
        self.k1 = k1
        self.b = b
        self._lock = asyncio.Lock()  # Add lock for thread-safe updates

    @property
    def papers(self) -> list[str]:
        return list(self._documents.keys())

    @property
    def number_of_documents(self) -> int:
        return len(self._documents)
    
    def _calculate_avdl(self) -> float:
        return sum(len(d) for d in self._documents.values()) / self.number_of_documents
    
    @property
    def avdl(self) -> float:
        if self._avdl is None:
            self._avdl = self._calculate_avdl()
        return self._avdl
    
    def idf(self, kw: str) -> float:
        N = self.number_of_documents
        n_kw = len(self.get_names(kw))
        return log((N - n_kw + 0.5) / (n_kw + 0.5) + 1)
    
    def bm25(self, kw: str) -> dict[str, float]:
        result = {}
        idf_score = self.idf(kw)
        avdl = self.avdl

        for name, freq in self.get_names(kw).items():
            numerator = freq * (self.k1 + 1)
            denominator = freq + self.k1 * (1 - self.b + self.b * len(self._documents[name]) / avdl)
            result[name] = idf_score * numerator / denominator
        
        return result
    
    def search(self, query: str) -> dict[str, float]:
        keywords = normalize_string(query).split(" ")
        name_scores: dict[str, float] = {}
        for kw in keywords:
            kw_names_score = self.bm25(kw)
            name_scores = update_name_scores(name_scores, kw_names_score)
        
        return name_scores

    async def _async_index(self, name: str, content: str) -> None:
        self._documents[name] = content
        words = normalize_string(content).split(" ")
        word_counts = defaultdict(int)

        # Counts freq locally first
        for word in words:
            word_counts[word] += 1
        
        # Update index atomically
        async with self._lock:
            for word, count in word_counts.items():
                self._index[word][name] += count

    async def async_bulk_index(self, documents: list[tuple[str, str]]):
        tasks = [self._async_index(name, content) for name, content in documents]
        await asyncio.gather(*tasks)

        self._avdl = None
    
    def bulk_index(self, documents: list[tuple[str, str]]) -> None:
        asyncio.run(self.async_bulk_index(documents))
        
        
    def get_names(self, keyword: str) -> dict[str, int]:
        keyword = normalize_string(keyword)
        return self._index[keyword]
    


