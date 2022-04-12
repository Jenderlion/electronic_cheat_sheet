def get_api():
    try:
        with open('api.txt', 'r') as api_file:
            result = api_file.read()
            print(f'Bot started with API-key: "{result}"\n'
                  f'If you want to replace API-key, delete api.txt file.')
            return result
    except Exception:
        api_to_write = input('Please enter an API-key: ')
        with open('api.txt', 'w') as api_file:
            api_file.write(api_to_write)
        get_api()
