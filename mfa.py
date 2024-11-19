import hashlib
import base64
import asyncio
from websockets.asyncio.server import serve
import json 
import torch
import pickle
from facenet_pytorch import InceptionResnetV1, training


https://blog.miguelgrinberg.com/post/two-factor-authentication-with-flask

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[Required(), Length(1, 64)])
    password = PasswordField('Password', validators=[Required()])
    token = StringField('Token', validators=[Required(), Length(6, 6)])
    submit = SubmitField('Login')


def get_hash(s):
    hash_s = hashlib.sha3_512()
    hash_s.update(s.encode())
    print(hash_s.digest())
    return base64.urlsafe_b64encode(hash_s.digest())

def get_data(f_name):
    in_file = open(f_name, "rb")
    data = in_file.read()
    in_file.close()
    return data

model_ft = torch.load('train_model_full.pt',weights_only=False)
model_ft.eval()

AMOUNT_OF_IMAGES = 2
DIFFICULTY = AMOUNT_OF_IMAGES - 0.00001
PROB_THRESH = 0.9999

USER_DB = {
    "p1": {
        "password": "my secure password",
        "class_index": 0
    }
}

async def echo(websocket):
    await websocket.send(
        json.dumps({
            "image_count": AMOUNT_OF_IMAGES,
            "difficulty": DIFFICULTY
        })
    )
    
    images = None
    for i in range(AMOUNT_OF_IMAGES):
        image_tensor_pickle = await websocket.recv()
        print(image_tensor_pickle)
        image_tensor = pickle.loads(get_data(image_tensor_pickle))
        if images is None:
            images = image_tensor
        else:
            images = torch.stack([images,image_tensor],dim=0)
            
    outputs = model_ft(images.to('mps'))
    probs = torch.nn.functional.softmax(outputs, dim=1)

    uname = await websocket.recv()
    pw = await websocket.recv()
    class_index = USER_DB[uname]['class_index']
    
    all_mfa_pass = torch.all(probs[:,class_index] > PROB_THRESH)

    if all_mfa_pass and USER_DB[uname]['password'] == pw:
        await websocket.send('ok')
    else:
        await websocket.send('fail')
        
    await websocket.close()
    
async def main():
    async with serve(echo, "localhost", 5000) as server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())