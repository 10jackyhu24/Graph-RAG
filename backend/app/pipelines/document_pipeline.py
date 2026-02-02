from app.transformers.summarizer import summarize

class DocumentPipeline:
    def __init__(self):
        self.steps = [
            summarize
        ]