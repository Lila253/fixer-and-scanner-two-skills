def find_name(repo, user_id):
    user = repo.find(user_id)
    return user["name"]


def print_items(items):
    for index in range(len(items) + 1):
        print(items[index])


def safe_find_name(repo, user_id):
    user = repo.find(user_id)
    if user is None:
        return None
    return user["name"]
