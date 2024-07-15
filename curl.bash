curl -X POST "http://127.0.0.1:8001/api/v1/contest/contest-history/" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzIxMTIzMDcwLCJpYXQiOjE3MjEwMzY2NzAsImp0aSI6IjBmMzVmNmIzMWJlNDQ3Njc5N2JkNTljYWJlY2Q4Zjc3IiwidXNlcl9pZCI6Mn0.0GuDaU-lZXozJMNoOmAC0HaIfvhe6eUZLaYpgI_rJK8" \
-H "Content-Type: application/json" \
-d '{
    "id": 1212,
    "profile": 2,
    "name": "Contest Name",
    "fixture_id": 1221,
    "entry_amount": 50,
    "league": "Premier League",
    "pending": true,
    "completed": false,
    "total_points": 100,
    "position": 1,
    "won_amount": 100.00,
    "pool_price": 500,
    "players": [
        {"id": 5, "name": "Player 1", "image_url": "url1", "team_id": 1, "fixture_id": 1, "points": 10, "position": "Forward"},
        {"id": 6, "name": "Player 2", "image_url": "url2", "team_id": 2, "fixture_id": 2, "points": 20, "position": "Midfielder"}
    ]
}'



curl -X GET "http://127.0.0.1:8001/api/v1/contest/contest-history/121/" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzIxMTIzMDcwLCJpYXQiOjE3MjEwMzY2NzAsImp0aSI6IjBmMzVmNmIzMWJlNDQ3Njc5N2JkNTljYWJlY2Q4Zjc3IiwidXNlcl9pZCI6Mn0.0GuDaU-lZXozJMNoOmAC0HaIfvhe6eUZLaYpgI_rJK8"



curl -X PUT "http://127.0.0.1:8001/api/v1/contest/contest-history/121/update/" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzIxMTIzMDcwLCJpYXQiOjE3MjEwMzY2NzAsImp0aSI6IjBmMzVmNmIzMWJlNDQ3Njc5N2JkNTljYWJlY2Q4Zjc3IiwidXNlcl9pZCI6Mn0.0GuDaU-lZXozJMNoOmAC0HaIfvhe6eUZLaYpgI_rJK8" \
-H "Content-Type: application/json" \
-d '{
    "id": 121,
    "profile": 1,
    "name": "Updated Contest Name",
    "fixture_id": 123,
    "entry_amount": 50,
    "action_title": "Updated Action Title",
    "pending": false,
    "completed": true,
    "total_points": 150,
    "position": 1,
    "won_amount": 150.00,
    "pool_price": 600,
    "players": [
        {"id": 1, "name": "Player 1", "image_url": "url1", "team_id": 1, "fixture_id": 1, "points": 15, "position": "Forward"},
        {"id": 2, "name": "Player 2", "image_url": "url2", "team_id": 2, "fixture_id": 2, "points": 25, "position": "Midfielder"}
    ]
}'
