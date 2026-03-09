from fastapi import Body, FastAPI, Query, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import Optional

app = FastAPI()

BLOG_POST = [
    {'id': 1, 'title': 'Hola', 'content': 'Primero'},
    {'id': 2, 'title': 'Segundo post', 'content': 'Segundo'},
    {'id': 3, 'title': 'Django vs FasAPI', 'content': 'Aca el contenido'},
]


class PostBase(BaseModel):
    title: str
    content: Optional[str] = "Contenido por defecto"

class PostCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=5,
        max_length=100,
        description="Titulo del post (minimo 3 caracteres, maximo 100)",
        examples=["Mi primer post"]
    ),
    content: Optional[str] = Field(
        default="Contenido no disponible",
        min_length=10,
        description="Contenido del post (minimo de 10 caracteres)",
        examples=["Este es un contenido valido porque tiene 10 caracteres o mas 2"]
    )
    
    @field_validator("title")
    @classmethod
    def not_allowed_title(cls, value:str) -> str:
        if "spam" in value.lower():
            raise ValueError("El titulo no puede contener la palabra: 'spam'")
        return value
    

class PostUpdate(BaseModel):
    title: str
    content: Optional[str] = "Contenido por defecto"



@app.get("/")
def home():
    return { 'message': 'Bienvenidos a Mini Blog'}

@app.get("/posts")
def list_posts(query: str| None = Query(default=None, description='Texto para buscar por titulo')):
    
    if query:
        results = [ post for post in BLOG_POST if query.lower() in post['title'].lower()]
        # results = []
        # for post in BLOG_POST:
        #     if query.lower() in post['title'].lower():
        #         results.append(post)
        return {"data": results, 'query':query}
    return {"data": BLOG_POST}


@app.get("/posts/{post_id}")
def get_post(post_id: int, include_content: bool = Query(default=True, description='booleano para incluir el content en el json')):
    for post in BLOG_POST:
        if post['id'] == post_id:
            if include_content:
                return {'data': post}
            else:
                return {'data': {  
                    'id': post['id'],
                    'title': post['title']
                }}
    return {'error': 'Post no encontrado'}



@app.post("/posts")
def create_post(post : PostCreate):
    new_id = (BLOG_POST[-1]["id"]+1) if BLOG_POST else 1
    new_post = {"id": new_id, "title": post.title, "content": post.content}
    BLOG_POST.append(new_post)
    return {"message": "Post creado", "data": BLOG_POST}


@app.put("/posts/{post_id}")
def update_post(post_id: int, data: PostUpdate):
    for post in BLOG_POST:
        if post["id"] == post_id:
            payload = data.model_dump(exclude_unset=True)
            if "title" in payload: post["title"] = payload["title"]
            if "content" in payload: post["content"] = payload["content"]
            return {"message":"Post actualizado", "data": post }
    raise HTTPException(status_code=404, detail="No se encontro el post")
    # return {"error": "No se encontro el post"}


@app.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: int):
    for index,post in enumerate(BLOG_POST):
        if post["id"] == post_id:
            BLOG_POST.pop(index)
            return
    raise HTTPException(status_code=404, detail="Post no encontrado")
