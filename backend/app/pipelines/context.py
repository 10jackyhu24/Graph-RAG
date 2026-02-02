class PipelineContext:
    def __init__(self, file=None, text=None):
        self.file = file          # UploadFile
        self.raw_text = None      # Extracted text from the file
        self.summary = None       # LLM-generated summary
        self.pdf_bytes = None     # PDF bytes of the summary