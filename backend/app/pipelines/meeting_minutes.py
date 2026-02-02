class MeetingMinutesPipeline:
    steps = [
        "speech_to_text",
        "clean_text",
        "summarize",
        "export_docx"
    ]
