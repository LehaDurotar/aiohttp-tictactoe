# Tictactoe - rest api для игры крестики-нолики
## Первый запуск
1. `~ sudo docker-compose -f dev.docker-compose.yml up --build`

## Миграции с alembic
```
Создаем новую миграцию
~ docker-compose exec tictactoe_server alembic revision --autogenerate -m "create tables"
Мигрируем:
~ docker-compose exec tictactoe_server alembic upgrade head
Откатываемся:
~ docker-compose exec tictactoe_server alembic downgrade -1
```
## Пример использования
```
Воспользуемcя модулем python requests для тестирования сервиса, 
однако вы можете использовать что хотите.

~ requests.post("http://0.0.0.0:8080/register"", {"username": "player1", "password": "pass1"}).json()
~ requests.post("http://0.0.0.0:8080/register", {"username": "player2", "password": "pass2"}).json()
~ requests.post("http://0.0.0.0:8080/game", {"name": "testgame"}).json()
~ requests.get("http://0.0.0.0:8080/game/").json()
~ requests.post("http://0.0.0.0:8080/game/testgame/player", {"player_name": "player1").json()
~ requests.post("http://0.0.0.0:8080/game/testgame/player", {"player_name": "player2").json()
~ requests.post("http://0.0.0.0:8080/game/testgame/player/Player1/move", {"square": "1"}).json()
~ requests.post("http://0.0.0.0:8080/game/testgame/player/Player2/move", {"square": "2"}).json()
~ requests.get("http://0.0.0.0:8080/game/testgame/board").json()

```

## Описание методов API
#### Регистрирует нового игрока в БД
POST ```/register```
data: ```{username: <name>, password: <password>}```
#### Создает новую игру для игрока
POST ```/game/{game_name}/player```
data: ```{ 'player_name' : <a_name> }```
#### Сделать ход
POST ```/game/{game_name}/player/{player_name}/move```
data: ```{ 'square' : <a_number> }```
#### Показать инфо о всех играх
GET ```/game```
#### Показать всех зарегистрированных игроков
GET ```/player```
#### Показать текущее игровое поле
GET ```/game/{game_name}/board```

