curl -X POST "http://127.0.0.1:9000/api/v1/contest/contest-history/" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzIxODk5OTM5LCJpYXQiOjE3MjE4MTM1MzksImp0aSI6IjgxMGNkMzY5ODE1ZTQ2ZGM4NmMzNDlmMDk0NzM2ZjU0IiwidXNlcl9pZCI6Mn0.O_qEns55qnqGFZ_X2n9JHXVhcChdSr86aBfu-Q-a6CA" \
-H "Content-Type: application/json" \
-d '{
    "game_id": 3247,
    "fixture_id": 1234160,
    "profile": 2,
    "name": "Patriotas vs Fortaleza FC | Primera A",
    "entry_amount": 500000,
    "league": "Primera A",
    "pending": true,
    "completed": false,
    "total_points": 0,
    "position": 0,
    "won_amount": 0.00,
    "pool_price": 5000000,
    "max_entry" : 100,
    "players": [
        {"player_id": 13665, "name": "S. Román", "image_url": "https://media.api-sports.io/football/players/13665.png", "team_player_id": 1140, "fixture_player_id": 1234160, "points": 0, "position": "Goalkeeper"},
        {"player_id": 13728, "name": "J. Valencia", "image_url": "https://media.api-sports.io/football/players/13728.png", "team_player_id": 1140, "fixture_player_id": 1234160, "points": 0, "position": "Goalkeeper"},
        {"player_id": 353407, "name": "J. García", "image_url": "https://media.api-sports.io/football/players/353407.png", "team_player_id": 1140, "fixture_player_id": 1234160, "points": 0, "position": "Defender"},
        {"player_id": 459840, "name": "Fernando Torres", "image_url": "https://media.api-sports.io/football/players/459840.png", "team_player_id": 1140, "fixture_player_id": 1234160, "points": 0, "position": "Defender"},
        {"player_id": 354066, "name": "Samuel Edwardo Bello Vivas", "image_url": "https://media.api-sports.io/football/players/354066.png", "team_player_id": 1140, "fixture_player_id": 1234160, "points": 0, "position": "Defender"},
        {"player_id": 13799, "name": "B. Correa", "image_url": "https://media.api-sports.io/football/players/13799.png", "team_player_id": 1140, "fixture_player_id": 1234160, "points": 0, "position": "Defender"},
        {"player_id": 354788, "name": "A. Alarcón", "image_url": "https://media.api-sports.io/football/players/354788.png", "team_player_id": 1140, "fixture_player_id": 1234160, "points": 0, "position": "Midfielder"},
        {"player_id": 125678, "name": "J. Díaz", "image_url": "https://media.api-sports.io/football/players/125678.png", "team_player_id": 1140, "fixture_player_id": 1234160, "points": 0, "position": "Midfielder"}
    ]
}'
