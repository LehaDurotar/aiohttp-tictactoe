# def get_games():
#     all_games = Game.query.all()
#     result = games_schema.dump(all_games)
#     return jsonify(result
#
# #Show one game
# route('/games/<id>', methods=['GET'])
# def get_game_detail(id):
#     game_detail = Game.query.get(id)
#     #result = games_schema.dump(all_games)
#     return game_schema.jsonify(game_detail)
#
#
# # Update a game
# route('/games/<id>', methods=['PUT'])
# def update_game(id):
#     game = Game.query.get(id)
#
#     name = request.json['name']
#     status = request.json['status']
#     winner = request.json['winner']
#
#     game.name = name
#     game.status = status
#     game.winner = winner
#
#     db.session.commit()
#
#     return game_schema.jsonify(game)
#
# route('/games/<id>/moves', methods=['GET'])
# def get_game_status(id):
#
#     board = ['0','0','0','0','0','0','0','0','0']
#
#     game_detail = Game.query.get(id)
#
#     all_moves = Detail.query.filter(Detail.id_game == id).all()
#     results = details_schema.dump(all_moves)
#     for result in results:
#         result_list = list(result['moves'])
#         for i in range(len(result_list)):
#             if(result_list[i] == '1'):
#                 board[i] = result_list[i]
#             elif(result_list[i] == '2'):
#                 board[i] = result_list[i]
#
#
#     board_string = ''.join(board)
#
# print(game_detail.status, file=sys.stderr) return jsonify({"id":game_detail.id,"name":game_detail.name,
# "status":game_detail.status,"winner":game_detail.winner,"lastMove":board_string})
#
