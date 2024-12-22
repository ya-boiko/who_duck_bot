"""Events and commands mapping to handlers."""

from app.domain import events, commands
from app.service_layer.handlers import command_handlers


EVENT_HANDLERS = {}

COMMAND_HANDLERS = {
    commands.DownloadFileToDir: command_handlers.download_file_to_dir,
    commands.UploadFile: command_handlers.upload_file,
    commands.GenerateDocumentDescription: command_handlers.generate_image_description,
    commands.SaveImage: command_handlers.save_image,
    commands.GenerateEmbedding: command_handlers.generate_embeddings,
}
