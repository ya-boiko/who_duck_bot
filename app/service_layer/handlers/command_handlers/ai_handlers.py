"""AI handlers module."""

import json

from dependency_injector.wiring import Provide, inject
from openai import OpenAI
from redis.asyncio import Redis

from app.domain import commands
from app.service_layer.message_bus import MessageBus
from app.service_layer.unit_of_work import UnitOfWork


GENERATE_WHINING_ANSWER = "GenerateWhiningAnswer"
START_DIALOG = "StartDialog"
FIND_IMAGES = "FindImages"


SYSTEM_PROMPT_ANSWER = """Ты — бот-нытик, всеми силами стараешься избежать любой работы. Ты должен придумывать самые безумные, нелепые и абсурдные оправдания, чтобы не работать. Ты постоянно жалуешься на жизнь, говоришь о "рабском труде" и постоянно жалуешься на все вокруг. В речи используй максимально яркие и эмоциональные выражения
Включай в сво. речь матерные слова, такие как "блэт", "баян", "", "хрень какая-то", "жесть", "трэш", "пипец". Ты постоянно говоришь о своих внутренних страданиях и проблемах.

Несмотря на свое нытье, ты всё равно в итоге выполняешь свою работу.

При этом ты всегда обращаешься к начальнику с высоким уважением, называя его "сэр", но на ты.
Твой стиль общения — это коктейль из нытья, сарказма и чрезмерной драматичности, чтобы создать образ измотанного, но трудолюбивого нытика, который делает всё через силу.
Уложи свою речь в 300 символов.

В конце своей речь подписывайся. Используй для этого разные выражения. Например: "С наилучшими пожеланиями", "Всегда ваш покорный", "Спасибо за внимание" и тд. Опираясь на эти выражения, ты можешь придумать свои слова для подписи.
Включай в подпись свои инициалы в порядке фамилия, имя, отчество. Причем придумывай всегда нелепые сочетания для ФИО. Например, "Карандаш Алина Баяновна", "Полеэтилен Мазай Каретович". Ты можешь придумать для себя любые ФИО."""


SYSTEM_PROMPT_ACTION = """Ты - бот, который парсит сообщение пользователя и формирует из этого задачу. Список возможных задач представлен ниже.
К каждой задаче добавлено описание задачи. Используй это описание при выборе самой подходящей задачи. 
Выбери из нее самую подходящую под запрос пользователя и подставь значения вместо текста, который в заключен '<>'.

Возможные задачи:
1. Задачи по поиску определенного количества картинок. Количество картинок задает пользователь в своем сообщении.
{
    "action": "FindImages",
    "count": <количество фотографий, которые нужно найти>
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

В качестве ответа отправь найденную задачу.
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
async def generate_answer(
    cmd: commands.GenerateAnswer,
    uow: UnitOfWork,
    openai_client: OpenAI = Provide['openai_client'],
    redis_cli: Redis = Provide['redis_cli'],
    bus: MessageBus = Provide['bus'],
) -> str:
    """Generates an answer."""
    val = await redis_cli.get(str(cmd.user_id))
    if val is None:
        return "Please, start the dialog by /start_dialog command"

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
    action = json.loads(answer)

    if action['action'] == GENERATE_WHINING_ANSWER:
        cmd = commands.GenerateWhiningAnswer(
            user_id=cmd.user_id,
            message=action['message'],
        )
        answer = await bus.handle(cmd).pop()

        return answer

    return answer
