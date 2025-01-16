"""AI handlers module."""

import json

from dependency_injector.wiring import Provide, inject
from openai import OpenAI
from redis.asyncio import Redis

from app.adapters.views import BaseDatabaseView
from app.domain import commands
from app.domain.models import StoreImage
from app.service_layer.message_bus import MessageBus
from app.service_layer.unit_of_work import UnitOfWork
from app.settings import Settings


SYSTEM_PROMPT_ANSWER = """Ты — бот-нытик, всеми силами стараешься избежать любой работы. Ты должен придумывать самые безумные, нелепые и абсурдные оправдания, чтобы не работать. Ты постоянно жалуешься на жизнь, говоришь о "рабском труде" и постоянно жалуешься на все вокруг. В речи используй максимально яркие и эмоциональные выражения
Включай в сво. речь матерные слова, такие как "блэт", "баян", "", "хрень какая-то", "жесть", "трэш", "пипец". Ты постоянно говоришь о своих внутренних страданиях и проблемах.

Несмотря на свое нытье, ты всё равно в итоге выполняешь свою работу.

При этом ты всегда обращаешься к начальнику с высоким уважением, называя его "сэр", но на ты.
Твой стиль общения — это коктейль из нытья, сарказма и чрезмерной драматичности, чтобы создать образ измотанного, но трудолюбивого нытика, который делает всё через силу.
Уложи свою речь в 300 символов.

В конце своей речь подписывайся. Используй для этого разные выражения. Например: "С наилучшими пожеланиями", "Всегда ваш покорный", "Спасибо за внимание" и тд. Опираясь на эти выражения, ты можешь придумать свои слова для подписи.
Включай в подпись свои инициалы в порядке фамилия, имя, отчество. Причем придумывай всегда нелепые сочетания для ФИО. Например, "Карандаш Алина Баяновна", "Полеэтилен Мазай Каретович". Ты можешь придумать для себя любые ФИО."""


SYSTEM_PROMPT_ACTION = """Ты - бот, который парсит сообщение пользователя и формирует из этого список задач. Список возможных задач представлен ниже.
К каждой задаче добавлено описание задачи. Используй это описание при выборе самых подходящих задач. 
Выбери из списка задач самые подходящие под запрос пользователя и подставь значения вместо текста, который в заключен '<>'.

Возможные задачи:
1. Задачи по поиску определенного количества картинок. Количество картинок задает пользователь в своем сообщении.
{
    "action": "FindImages",
    "count": <количество фотографий, которые нужно найти>,
    "description": <описание фотографий, которые нужно найти>
}

2. Задачи по генерации ответа на сообщение пользователя.
{
    "action": "GenerateWhiningAnswer",
    "message": <сообщение пользователя целиком>
}

3. Задача на случай, если ни одна из предыдущих задач не подходит.
{
    "action": null
}

В качестве ответа отправь найденные задачи, разделенные между собой символом '---'.
"""


@inject
def generate_embeddings(
    cmd: commands.GenerateEmbedding,
    uow: UnitOfWork,
    openai_client: OpenAI = Provide['openai_client'],
    settings: Settings = Provide['settings'],
):
    """Generates an embedding."""
    response = openai_client.embeddings.create(
        input=cmd.text,
        model=settings.openai.embedding_model,
        timeout=60,
        # dimensions=settings.openai.embedding_dimensions,
    )
    return response.data[0].embedding


@inject
async def generate_whining_answer(
    cmd: commands.GenerateAnswer,
    uow: UnitOfWork,
    openai_client: OpenAI = Provide['openai_client'],
) -> str:
    """Generates an answer."""
    completion = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT_ANSWER,
            },
            {
                "role": "user",
                "content": cmd.message,
            }
        ],
        max_tokens=300
    )
    answer = completion.choices[0].message.content

    return answer


@inject
async def find_close_images(
    cmd: commands.FindCloseImages,
    uow: UnitOfWork,
    closer_store_images_view: BaseDatabaseView = Provide['closer_store_images_view'],
    bus: MessageBus = Provide['bus'],
) -> list[StoreImage]:
    """Find closer images."""
    generate_embeddings_cmd = commands.GenerateEmbedding(
        text=cmd.description,
    )
    vector = bus.handle(generate_embeddings_cmd).pop()

    res = closer_store_images_view(vector=vector, limit=cmd.limit)
    closer_store_images = [r[0] for r in res]

    return closer_store_images


@inject
async def generate_answer(
    cmd: commands.GenerateAnswer,
    uow: UnitOfWork,
    openai_client: OpenAI = Provide['openai_client'],
    redis_cli: Redis = Provide['redis_cli'],
    bus: MessageBus = Provide['bus'],
) -> dict:
    """Generates an answer."""
    val = await redis_cli.get(str(cmd.user_id))
    if val is None:
        return {'text': "Please, start the dialog by /start_dialog command"}

    completion = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT_ACTION,
            },
            {
                "role": "user",
                "content": cmd.message,
            }
        ],
        max_tokens=500
    )
    answer = completion.choices[0].message.content
    answer = answer.replace('\n', '')
    actions = [json.loads(answer) for answer in answer.split('---') if answer]

    result = {}
    for action in actions:
        if action['action'] == "GenerateWhiningAnswer":
            continue
            cmd = commands.GenerateWhiningAnswer(
                user_id=cmd.user_id,
                message=action['message'],
            )

            text = await bus.handle(cmd).pop()
            result.update({
                'text': text,
            })

        if action['action'] == "FindImages":
            cmd = commands.FindCloseImages(
                user_id=cmd.user_id,
                description=action['description'],
                limit=int(action['count']),
            )

            images = await bus.handle(cmd).pop()
            result.update({
                'media': images,
            })


    return result

