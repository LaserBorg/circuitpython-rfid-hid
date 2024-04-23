import json

# READ known_tags from JSON
def get_tags_dict(json_path):
    with open(json_path, 'r') as file:
        known_tags = json.load(file)
    return known_tags


if __name__ == "__main__":
    known_tags = get_tags_dict('circuitpython/known_tags.json')
    print(known_tags) 
    # {"0x4348b603": "WHITE CARD", "0x09a929b3": "BLUE TOKEN"}
  