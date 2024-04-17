def read_counter(file_path):
    try:
        with open(file_path, "r") as file:
            content = file.read().strip()
            return int(content) if content else 0
    except FileNotFoundError:
        return 0
    except ValueError:
        print(f"Warning: Unexpected content in {file_path}. Resetting to 0.")
        return 0


def increment_counter(file_path):
    count = read_counter(file_path) + 1
    with open(file_path, "w") as file:
        file.write(str(count))
    return count
