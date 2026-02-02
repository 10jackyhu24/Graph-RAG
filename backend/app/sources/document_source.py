from app.utils.file_parser import parse_file

class DocumentSource:
    def __init__(self, file):
        self.file = file

    async def load(self):
        return await parse_file(self.file)
