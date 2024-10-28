import base64

def obfuscate_chat_id(chat_id):
    # Convert the chat_id to bytes and then encode to base64
    chat_id_bytes = str(chat_id).encode('utf-8')
    obfuscated_id = base64.urlsafe_b64encode(chat_id_bytes).decode('utf-8')
    return obfuscated_id

def deobfuscate_chat_id(obfuscated_id):
    # Decode the base64 string back to the original chat_id
    decoded_bytes = base64.urlsafe_b64decode(obfuscated_id)
    chat_id = int(decoded_bytes.decode('utf-8'))
    return chat_id
