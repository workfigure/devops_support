from llama_index.readers.web import BeautifulSoupWebReader

class WebReader:
    def __init__(self, urls: str):
        self.urls = urls
        self.documents = None

    def _load_data(self):
        # Load data from the provided URLs using the BeautifulSoupWebReader
        loader = BeautifulSoupWebReader()
        print(f"Loading documents from URLs: {self.urls}")
        documents = loader.load_data(urls=[self.urls])
        return documents

    def get_documents(self):
        if self.documents is None:
            self.documents = self._load_data()
        return self.documents


class ArgoWebReader(WebReader):
    def __init__(self, urls="https://argoproj.github.io/cd"):
        super().__init__(urls)
