"""Events and commands mapping to handlers."""

from app.domain import events, commands
from app.service_layer.handlers import command_handlers


EVENT_HANDLERS = {}

COMMAND_HANDLERS = {
    commands.DownloadFileToDir: command_handlers.download_file_to_dir,

    commands.UploadFile: command_handlers.upload_file,
    commands.DownloadFile: command_handlers.download_file,

    commands.SaveImage: command_handlers.save_image,
    commands.StartDialog: command_handlers.start_dialog,
    commands.FinishDialog: command_handlers.finish_dialog,

    commands.GenerateEmbedding: command_handlers.generate_embeddings,
    commands.GenerateDocumentDescription: command_handlers.generate_image_description,
    commands.GenerateAnswer: command_handlers.generate_answer,
    commands.GenerateWhiningAnswer: command_handlers.generate_whining_answer,
    commands.FindCloseImages: command_handlers.find_close_images,
}
