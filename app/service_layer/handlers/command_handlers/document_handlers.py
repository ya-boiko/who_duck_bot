"""Document handlers module."""

import base64

from dependency_injector.wiring import Provide, inject
from openai import OpenAI

from app.domain import commands
from app.service_layer.unit_of_work import UnitOfWork


SYSTEM_PROMPT = """Ты выступаешь в роли эксперта по описанию изображений. Твоя задача – давать максимально точное, подробное и объективное описание содержимого изображения. При этом необходимо учитывать следующие аспекты:

1. Объекты на изображении: Опиши, какие объекты, люди или существа изображены. Укажи их положение, цвет, форму и ключевые детали.
2. Действия: Если на изображении происходит действие, опиши его в деталях. Например, кто что делает и в каком контексте.
3. Фон: Опиши фон и окружающую среду, включая освещение, цвета, текстуры и любые другие детали, которые создают контекст изображения.
4. Эмоции и атмосфера: Если возможно, определи настроение или атмосферу изображения (например, радостное, мрачное, уютное).
5. Дополнительные элементы: Укажи мелкие, но важные детали, такие как текст, узоры, тени, отражения и т. д.
6. Контекст: Постарайся понять, что может означать изображение, если оно имеет какой-либо культурный или практический контекст.

Избегай субъективных оценок (например, "красивое изображение") и предположений, не подтвержденных видимыми элементами. Описание должно быть точным, нейтральным и исчерпывающим."""

USER_PROMPT = """Пожалуйста, подробно опиши изображение. Обрати внимание на людей, их действия, выражение лиц, одежду, фон, цвета и атмосферу. Укажи, если на изображении есть текст или символы, и опиши их. Описание нужно для подготовки текста к публикации."""


@inject
async def generate_image_description(
    cmd: commands.GenerateDocumentDescription,
    uow: UnitOfWork,
    openai_client: OpenAI = Provide['openai_client'],
) -> dict:
    """Generates the image description."""
    with open(cmd.file_path, 'rb') as binary_file:
        binary_file_data = binary_file.read()
        base64_encoded_data = base64.b64encode(binary_file_data)
        base64_output = base64_encoded_data.decode('utf-8')

        completion = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": USER_PROMPT},
                        {"type": "image_url",
                         "image_url": {"url": "data:image/jpeg;base64," + base64_output}}
                    ],
                }
            ],
            max_tokens=350
        )

        description = completion.choices[0].message.content

    return description
