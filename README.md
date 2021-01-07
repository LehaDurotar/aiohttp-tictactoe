# Tictactoe - rest api для игры крестики-нолики
## Запуск в контейнере
1. `~ sudo docker-compose up -d`


## Пример использования
```
Воспользуемcя модулем python requests для тестирования сервиса, 
однако вы можете использовать что хотите.

~ requests.post("http://0.0.0.0:8080/auth/signup", {"username": "player1", "password": "pass1"}).json()
~ requests.post("http://0.0.0.0:8080/auth/signup", {"username": "player2", "password": "pass2"}).json()
~ requests.post("http://0.0.0.0:8080/game/", {"name": "testgame"}).json()
~ requests.get("http://0.0.0.0:8080/game/").json()
~ requests.post("http://0.0.0.0:8080/game/testgame/player", {"player_name": "player1").json()
~ requests.post("http://0.0.0.0:8080/game/testgame/player", {"player_name": "player2").json()
~ requests.post("http://0.0.0.0:8080/game/testgame/player/Player1/move", {"square": "1"}).json()
~ requests.post("http://0.0.0.0:8080/game/testgame/player/Player2/move", {"square": "2"}).json()
~ requests.get("http://0.0.0.0:8080/game/testgame/board").json()

```

## Описание методов API
#### Регистрирует нового игрока в БД
POST ```/auth/signup```
data: ```{username: <name>, password: <password>}```
#### Авторизация
POST ```/auth/login```
data: ```{username: <name>, password: <password>}```
#### Логаут
GET ```/auth/logout```
#### Создает новую игру для игрока
POST ```/game/{game_name}/player```
data: ```{ 'player_name' : <a_name> }```
#### Сделать ход
POST ```/game/{game_name}/player/{player_name}/move```
data: ```{ 'square' : <a_number> }```
#### Показать инфо о всех играх
GET ```/game```
#### Показать всех зарегистрированных игроков
GET ```/game/player```
#### Показать текущее игровое поле
GET ```/game/{game_name}/board```

