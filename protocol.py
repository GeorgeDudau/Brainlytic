# Format for understanding between computers
import json 

# Converts data to dictionary
def encode(messageType, data):

    return json.dumps({ 
        "type": messageType,
        "data": data
    # Converts string to bytes so it can be sent
    }).encode() 

# Converts from bytes to string
def decode(data):
    return json.loads(data.decode()) 