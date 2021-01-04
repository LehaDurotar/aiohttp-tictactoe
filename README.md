# Tictactoe - rest api для игры крестики-нолики
## Первый запуск
1. `~ docker-compose up -d --build`
1. `~ docker-compose exec web alembic upgrade head`

## Миграции с alembic
```
Создаем новую миграцию
~ docker-compose exec web alembic revision --autogenerate -m "create tables"
Мигрируем:
~ docker-compose exec web alembic upgrade head
Откатываемся:
~ docker-compose exec web alembic downgrade -1
```

## Описание методов API
```

```

