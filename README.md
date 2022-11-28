# Реализация и взаимодействие с API:
    ## Стек:
        - FastAPI - реализация апи,
        - PonyORM - orm для работы с бд,
        - Postman, Thunder Client - тестирование API,
        - Bit - работа с Биткоинами,
        - pyTelegramBotAPI - реализация Тг-бота,
        - pydantic - валидация

    Для корректной работы необходимы две переменные
        config.py:
            bot_token - токен бота, у которого будет реализован функционал
            tg_admin_id - ваш телеграмм id

    Проект не закончен, осталась:
        - работа над безопасностью приложения,
        - тестирование,
        - загрузка API и клиента в облако,
        - реализовать домен
