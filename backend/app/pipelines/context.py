class PipelineContext:
    def __init__(
        self,
        file=None,
        text=None,
        tenant_id="default",
        source_type=None,
        llm_provider=None,
        llm_model=None,
        agent_id=None,
    ):
        self.file = file          # UploadFile
        self.text = text          # Raw text input
        self.tenant_id = tenant_id
        self.source_type = source_type
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.agent_id = agent_id

        self.raw_text = None      # Extracted text from the file
        self.markdown = None      # Layout-aware markdown (PDF)
        self.ifc_components = None
        self.summary = None       # LLM-generated summary
        self.extraction = None    # Structured extraction (Pydantic)
        self.storage_result = None
        self.agent = None         # Agent config dict
        self.source_path = None   # Uploaded file path

        self.pdf_bytes = None     # PDF bytes of the summary
        self.pdf_json = None      # PDF JSON structure for viewer
