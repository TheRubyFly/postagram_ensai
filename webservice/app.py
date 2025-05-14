#################################################################################################
##                                                                                             ##
##                                 NE PAS TOUCHER CETTE PARTIE                                 ##
##                                                                                             ##
## 👇 👇 👇 👇 👇 👇 👇 👇 👇 👇 👇 👇 👇 👇 👇 👇 👇 👇 👇 👇 👇 👇 👇 👇 👇 👇 👇 👇 👇 👇 ##
import boto3
from botocore.config import Config
import os
import uuid
from dotenv import load_dotenv
from typing import Union
import logging
from fastapi import FastAPI, Request, status, Header
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from getSignedUrl import getSignedUrl

load_dotenv()

app = FastAPI()
logger = logging.getLogger("uvicorn")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
	exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
	logger.error(f"{request}: {exc_str}")
	content = {'status_code': 10422, 'message': exc_str, 'data': None}
	return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class Post(BaseModel):
    title: str
    body: str

my_config = Config(
    region_name='us-east-1',
    signature_version='v4',
)

dynamodb = boto3.resource('dynamodb', config=my_config)
table = dynamodb.Table(os.getenv("DYNAMO_TABLE"))
s3_client = boto3.client('s3', config=boto3.session.Config(signature_version='s3v4'))
bucket = os.getenv("BUCKET")

## ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ##
##                                                                                                ##
####################################################################################################


@app.post("/posts")
async def post_a_post(post: Post, authorization: str | None = Header(default=None)):
    """
    Poste un post ! Les informations du poste sont dans post.title, post.body et le user dans authorization
    """
    logger.info(f"title : {post.title}")
    logger.info(f"body : {post.body}")
    logger.info(f"user : {authorization}")

    post_id = str(uuid.uuid4())
    image_link = getSignedUrl(bucket, f"{authorization}/{post_id}/image.png")

    item = {
        'user': f"USER#{authorization}",
        'post_id': post_id,
        'post_content': post.body,
        'post_title': post.title,
        'post_image': image_link,
    }


    logger.info(f"Inserting item in DynamoDB: {item}")

    # Insert dans DynamoDB
    table.put_item(Item=item)
    
    return {
        'post_id': post_id,
        'user': authorization,
        'title': post.title,
        'body': post.body
    }

@app.get("/posts")
async def get_posts(user: Union[str, None] = None):
    """
    Récupère tout les postes. 
    - Si un user est présent dans le requête, récupère uniquement les siens
    - Si aucun user n'est présent, récupère TOUS les postes de la table !!
    """
    if user :
        logger.info(f"Récupération des postes de : {user}")
        res = table.query(
            Select='ALL_ATTRIBUTES',
            KeyConditionExpression="#usr = :user",
            ExpressionAttributeNames={
                "#usr": "user"
            },
            ExpressionAttributeValues={
                ":user": f"USER#{user}",
            },
        )

    else :
        logger.info("Récupération de tous les postes")
        res = table.scan()

    items = res.get("Items", [])
    posts = []
    for item in items:
        post = {
            "user": item.get("user", "").replace("USER#", ""),
            "id": item.get("post_id"),
            "title": item.get("post_title"),
            "body": item.get("post_content"),
            "image": item.get("post_image"),
            "label": item.get("label", []),  # valeur par défaut vide
        }
        posts.append(post)

    logger.info(f"Nombre de posts renvoyés : {len(posts)}")
    return posts

    
@app.delete("/posts/{post_id}")
async def delete_post(post_id: str, request: Request, authorization: str | None = Header(default=None)):
    # Doit retourner le résultat de la requête la table dynamodb
    logger.info(f"RAW path params: {request.path_params}")
    logger.info(f"Full URL: {request.url}")
    logger.info(f"Method: {request.method}")
    logger.info(f"Headers: {request.headers}")
    logger.info(f"post_id : {post_id}")
    logger.info(f"user: {authorization}")

    # Récupération des infos du poste
    response = table.get_item(
        Key={
            'user': f"USER#{authorization}",
            'post_id': post_id
        }
    )

    item = response.get('Item', None)
    if not item:
        return JSONResponse(
            status_code=404,
            content={"message": "Post not found"}
        )
    # S'il y a une image on la supprime de S3

    # Suppression de la ligne dans la base dynamodb
    delete_response = table.delete_item(
        Key={
            'user': f"USER#{authorization}",
            'post_id': post_id
        }
    )
    # Retourne le résultat de la requête de suppression
    return "Post deleted succesfully"



#################################################################################################
##                                                                                             ##
##                                 NE PAS TOUCHER CETTE PARTIE                                 ##
##                                                                                             ##
## 👇 👇 👇 👇 👇 👇 👇 👇 👇 👇 👇 👇 👇 👇 👇 👇 👇 👇 👇 👇 👇 👇 👇 👇 👇 👇 👇 👇 👇 👇 ##
@app.get("/signedUrlPut")
async def get_signed_url_put(filename: str,filetype: str, postId: str,authorization: str | None = Header(default=None)):
    return getSignedUrl(filename, filetype, postId, authorization)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="debug")

## ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ☝️ ##
##                                                                                                ##
####################################################################################################


