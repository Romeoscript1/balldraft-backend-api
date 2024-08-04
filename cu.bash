curl -X POST "http://127.0.0.1:8000/api/v1/contest/contest-history/" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzIyNzg0MzEyLCJpYXQiOjE3MjI2OTc5MTIsImp0aSI6IjY5ZWNmMTdiMTMzZjQwNzE4MzU3NWJlZTE2YzQyOGNmIiwidXNlcl9pZCI6MX0.gCqMwwO8_3_ys8S6RojEl-ZtJrKFuoU7JUJi8eCp5zs" \
-H "Content-Type: application/json" \
-d '{
    "game_id": 3002,
    "fixture_id": 1234160,
    "profile": 1,
    "name": "Patriotas vs Fortaleza FC | Primera A",
    "entry_amount": 5000,
    "league": "Primera A",
    "pending": true,
    "completed": false,
    "total_points": 0,
    "position": 0,
    "won_amount": 0.00,
    "pool_price": 5000000,
    "max_entry" : 100,
    "players": [
        {"player_id": 79163, "name": "S. Román", "image_url": "https://media.api-sports.io/football/players/13665.png", "team_player_id": 1140, "fixture_player_id": 1234160, "points": 0, "position": "Goalkeeper"},
        {"player_id": 52590, "name": "J. Amaya", "image_url": "https://media.api-sports.io/football/players/299736.png", "team_player_id": 1140, "fixture_player_id": 1234160, "points": 0, "position": "Goalkeeper"},
        {"player_id": 352514, "name": "J. Valencia", "image_url": "https://media.api-sports.io/football/players/13728.png", "team_player_id": 1140, "fixture_player_id": 1234160, "points": 0, "position": "Goalkeeper"},
        {"player_id": 52590, "name": "J. Arce", "image_url": "https://media.api-sports.io/football/players/303898.png", "team_player_id": 1140, "fixture_player_id": 1234160, "points": 0, "position": "Defender"},
        {"player_id": 265961, "name": "Juan José Guevara Possu", "image_url": "https://media.api-sports.io/football/players/59810.png", "team_player_id": 1140, "fixture_player_id": 1234160, "points": 0, "position": "Defender"},
        {"player_id": 64215, "name": "C. Charris", "image_url": "https://media.api-sports.io/football/players/324727.png", "team_player_id": 1140, "fixture_player_id": 1234160, "points": 0, "position": "Defender"},
        {"player_id": 59642, "name": "J. Guerrero", "image_url": "https://media.api-sports.io/football/players/353428.png", "team_player_id": 1140, "fixture_player_id": 1234160, "points": 0, "position": "Defender"},
        {"player_id": 196851, "name": "C. De Las Salas", "image_url": "https://media.api-sports.io/football/players/59802.png", "team_player_id": 1140, "fixture_player_id": 1234160, "points": 0, "position": "Defender"}
    ]
}'


