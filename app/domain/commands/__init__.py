"""Commands."""

from .command import Command
from .tg_commands import DownloadFileToDir
from .yandex_commands import UploadFile, DownloadFile
from .bot_commands import SaveImage, StartDialog, FinishDialog
from .ai_commands import (
    GenerateEmbedding,
    GenerateDocumentDescription,
    GenerateAnswer,
    GenerateWhiningAnswer,
    FindCloseImages
)
