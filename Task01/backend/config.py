import os

# To declare global environment variables
class Config:
    DOCUMENT_FOLDER = os.path.join(os.path.dirname(__file__), 'documents')
