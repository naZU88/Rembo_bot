import json


data = [
    {"user_id": 12345,
     "user_voc": {
         "stone": ["kamen", "Use this stone carefully"]}
         }
]

users_id = [id['user_id'] for id in data]
print(users_id)


# with open('users_data.json', 'w', encoding='utf-8') as f:
#     json.dump(data, f, indent=2)

# with open('users_data.json') as file:
#     data = json.load(file)
