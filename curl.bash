curl -X POST "http://127.0.0.1:9000/api/v1/contest/contest-history/" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzIxODE1NDQ3LCJpYXQiOjE3MjE3MjkwNDcsImp0aSI6ImI3NGFlODRiMGYzNzRiNWE4ZmFjY2QyY2Q5NWU2NzA1Iiwplayer_idXNlcl9pZCI6MX0.JBXIFHmQae8oyVQFO9AzrKo2S7yOiiT4Xis0IL3Ryhg" \
-H "Content-Type: application/json" \
-d '{
    "player_id": 85,
    "fixture_player_id": 1234466,
    "profile": 1,
    "name": "Independiente de La Chorrera vs Herrera | Liga Panameña de Fútbol",
    "entry_amount": 500000,
    "league": "Liga Panameña de Fútbol",
    "pending": true,
    "completed": false,
    "total_points": 0,
    "position": 0,
    "won_amount": 0.00,
    "pool_price": 1000000,
    "players": [
        {"player_player_id": 325983, "name": "F. Núñez", "image_url": "https://media.api-sports.io/football/players/325983.png", "team_player_id": 2890, "fixture_player_id": 85, "points": 0, "position": "Goalkeeper"},
        {"player_player_id": 57725, "name": "E. Roberts", "image_url": "https://media.api-sports.io/football/players/57725.png", "team_player_id": 2890, "fixture_player_id": 85, "points": 0, "position": "Goalkeeper"},
        {"player_player_id": 360986, "name": "M. Sánchez", "image_url": "https://media.api-sports.io/football/players/360986.png", "team_player_id": 2890, "fixture_player_id": 85, "points": 0, "position": "Goalkeeper"},
        {"player_player_id": 57801, "name": "A. Ariano", "image_url": "https://media.api-sports.io/football/players/57801.png", "team_player_id": 2890, "fixture_player_id": 85, "points": 0, "position": "Defender"},
        {"player_player_id": 439661, "name": "C. Avila Aguirre", "image_url": "https://media.api-sports.io/football/players/439661.png", "team_player_id": 2890, "fixture_player_id": 85, "points": 0, "position": "Defender"},
        {"player_player_id": 304057, "name": "O. Davis", "image_url": "https://media.api-sports.io/football/players/304057.png", "team_player_id": 2890, "fixture_player_id": 85, "points": 0, "position": "Defender"},
        {"player_player_id": 444697, "name": "A. Gudiño", "image_url": "https://media.api-sports.io/football/players/444697.png", "team_player_id": 2890, "fixture_player_id": 85, "points": 0, "position": "Defender"},
        {"player_player_id": 407107, "name": "J. Modelo", "image_url": "https://media.api-sports.io/football/players/407107.png", "team_player_id": 2890, "fixture_player_id": 85, "points": 0, "position": "Defender"}
    ]
}'



curl -X POST "http://127.0.0.1:9000/api/v1/contest/contest-history/" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzIxODk5OTM5LCJpYXQiOjE3MjE4MTM1MzksImp0aSI6IjgxMGNkMzY5ODE1ZTQ2ZGM4NmMzNDlmMDk0NzM2ZjU0IiwidXNlcl9pZCI6Mn0.O_qEns55qnqGFZ_X2n9JHXVhcChdSr86aBfu-Q-a6CA" \
-H "Content-Type: application/json" \
-d '{
    "game_id": 3247,
    "fixture_player_id": 1234160,
    "profile": 2,
    "name": "Patriotas vs Fortaleza FC | Primera A",
    "entry_amount": 500000,
    "league": "Primera A",
    "pending": true,
    "completed": false,
    "total_points": 0,
    "position": 0,
    "won_amount": 0.00,
    "pool_price": 1000000,
    "players": [
        {"player_id": 13665, "name": "S. Román", "image_url": "https://media.api-sports.io/football/players/13665.png", "team_player_id": 1140, "fixture_player_id": 1234160, "points": 0, "position": "Goalkeeper"},
        {"player_id": 299736, "name": "J. Amaya", "image_url": "https://media.api-sports.io/football/players/299736.png", "team_player_id": 1140, "fixture_player_id": 1234160, "points": 0, "position": "Goalkeeper"},
        {"player_id": 13728, "name": "J. Valencia", "image_url": "https://media.api-sports.io/football/players/13728.png", "team_player_id": 1140, "fixture_player_id": 1234160, "points": 0, "position": "Goalkeeper"},
        {"player_id": 303898, "name": "J. Arce", "image_url": "https://media.api-sports.io/football/players/303898.png", "team_player_id": 1140, "fixture_player_id": 1234160, "points": 0, "position": "Defender"},
        {"player_id": 59810, "name": "D. Rodas", "image_url": "https://media.api-sports.io/football/players/59810.png", "team_player_id": 1140, "fixture_player_id": 1234160, "points": 0, "position": "Defender"},
        {"player_id": 324727, "name": "C. Charris", "image_url": "https://media.api-sports.io/football/players/324727.png", "team_player_id": 1140, "fixture_player_id": 1234160, "points": 0, "position": "Defender"},
        {"player_id": 353428, "name": "J. Guerrero", "image_url": "https://media.api-sports.io/football/players/353428.png", "team_player_id": 1140, "fixture_player_id": 1234160, "points": 0, "position": "Defender"},
        {"player_id": 59802, "name": "C. De Las Salas", "image_url": "https://media.api-sports.io/football/players/59802.png", "team_player_id": 1140, "fixture_player_id": 1234160, "points": 0, "position": "Defender"}
    ]
}'
