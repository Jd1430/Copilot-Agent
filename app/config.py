import toml

def get_secret(secret_name):
    try:
        secrets = toml.load(".streamlit/secrets.toml")
        return secrets.get(secret_name)
    except Exception as e:
        print(f"Error loading secret: {e}")
        return None
