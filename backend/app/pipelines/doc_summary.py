class DocumentSummaryPipeline:
    steps = [
        "parse_document",
        "summarize",
        "export_pdf"
    ]
