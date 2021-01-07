# Tictactoe - rest api для игры крестики-нолики
## Запуск в контейнере
1. `~ sudo docker-compose up`


## Пример использования
```
Воспользуемcя модулем python requests для тестирования сервиса

~ post("http://0.0.0.0:8080/auth/signup", {"username": "testuser", "password": "1234"}).json()
~ {'success': 'User testuser is created!'}
~ get("http://0.0.0.0:8080/auth/").json()
~ {'error': 'Auth Required!'}
~ post("http://0.0.0.0:8080/auth/login", {"username":"testuser", "password":"1234"}).json()
~ {'success': 'Welcome testuser'}
~ post("http://0.0.0.0:8080/game/", {"name": "testgame"}).json()
~ {'success': 'New Game: testgame has been created'}
~ post("http://0.0.0.0:8080/game/testgame/player", {"username": "player1"}).json()
~ {'success': {'new player': 'New player: player1 has been added to game: testgame and is using crosses '}}
~ post("http://0.0.0.0:8080/game/testgame/player", {"username": "computer"}).json()
~ {'success': {'new player': 'New player: computer has been added to game: testgame and is using noughts '}}
~ post("http://0.0.0.0:8080/game/testgame/player/player1/move", {"square": "1"}).json()
~ {'success': [{'player1': 'Moved an X to square 1'}, {'computer': 'Moved an O to square 7'}]}
~ post("http://0.0.0.0:8080/game/testgame/player/player1/move", {"square": "2"}).json()
~ {'success': [{'player1': 'Moved an X to square 2'}, {'computer': 'Moved an O to square 8'}]}
...
~ {'success': {'player1': 'Congratulations You won the game.'}}
~ get("http://0.0.0.0:8080/game/testgame/board").json()
~ {'success': {'1': 'X', '7': 'O', '2': 'X', '8': 'O', '3': 'X'}}
~ get("http://0.0.0.0:8080/auth/logout").json()
~ {'error': 'Auth Required!'}


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
#### Создает новую игровую сессию
POST ```/game/```
data: ```{ 'name' : <game_name> }```
#### Добавляет нового игрока в существующую игру
POST ```/game/{game_name}/player```
data: ```{ 'player_name' : <name> }```
#### Сделать ход
POST ```/game/{game_name}/player/{player_name}/move```
data: ```{ 'square' : <number> }```
#### Показать инфо о всех играх
GET ```/game```
#### Показать всех зарегистрированных игроков
GET ```/game/player```
#### Показать текущее игровое поле
GET ```/game/{game_name}/board```

