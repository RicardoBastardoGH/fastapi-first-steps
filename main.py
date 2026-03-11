from fastapi import Body, FastAPI, Query, HTTPException
from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import List, Optional, Union

app = FastAPI()

BLOG_POST = [
    {'id': 1, 'title': 'Hola', 'content': 'Primero'},
    {'id': 2, 'title': 'Segundo post', 'content': 'Segundo'},
    {'id': 3, 'title': 'Django vs FasAPI', 'content': 'Aca el contenido'},
]

NOT_ALLOWED_WORDS: list[str] = [
    "spam", "price","click"
]

class Tag(BaseModel):
    name: str = Field(..., min_length=2, max_length=30, description="Nombre de la etiqueta")

class Author(BaseModel):
    name: str = Field(..., min_length=2, max_length=30, description="Nombre del autor")
    email: EmailStr

class PostBase(BaseModel):
    title: str
    content: str
    tags: Optional[List[Tag]] = []
    author: Optional[Author] = None
     
    # content: Optional[str] = "Contenido por defecto"

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
    ),
    tags: List[Tag] = [],
    author: Optional[Author] = None
    
    @field_validator("title")
    @classmethod
    def not_allowed_title(cls, value:str) -> str:
        for word in NOT_ALLOWED_WORDS:
            if word in value.lower():
                raise ValueError(f"El titulo no puede contener la palabra: {word}")
        return value
    

class PostUpdate(BaseModel):
    title: str
    content: Optional[str] = "Contenido por defecto"

class PostPublic(PostBase):
    id: int

class PostSummary(BaseModel):
    id: int
    title: str


    
# class PostUpdate():

@app.get("/")
def home():
    return { 'message': 'Bienvenidos a Mini Blog'}

@app.get("/posts", response_model=List[PostPublic])
def list_posts(query: str| None = Query(default=None, description='Texto para buscar por titulo')):
    
    if query:
        return [ post for post in BLOG_POST if query.lower() in post["title"].lower() ]
        # results = [ post for post in BLOG_POST if query.lower() in post['title'].lower()]
        # results = []
        # for post in BLOG_POST:
        #     if query.lower() in post['title'].lower():
        #         results.append(post)
    return BLOG_POST


@app.get("/posts/{post_id}", response_model= Union[PostPublic, PostSummary], response_description="Post encontrado")
def get_post(post_id: int, include_content: bool = Query(default=True, description='booleano para incluir el content en el json')):
    for post in BLOG_POST:
        if post['id'] == post_id: 
            if include_content:
                return post
            else:
                return { 
                    'id': post['id'],
                    'title': post['title']
                }
    return HTTPException(status_code=404, detail="Post no encontrado")



@app.post("/posts",  response_model=PostPublic, description="Post creado (OK)")
def create_post(post : PostCreate):
    new_id = (BLOG_POST[-1]["id"]+1) if BLOG_POST else 1
    new_post = {"id": new_id, 
                "title": post.title, 
                "content": post.content, 
                "tags":[ tag.model_dump() for tag in post.tags],
                "author": post.author.model_dump() if post.author else None
                }
    BLOG_POST.append(new_post)
    return new_post


@app.put("/posts/{post_id}", response_model=PostPublic, description="Post actualizado", response_model_exclude_none=True)
def update_post(post_id: int, data: PostUpdate):
    for post in BLOG_POST:
        if post["id"] == post_id:
            payload = data.model_dump(exclude_unset=True)
            if "title" in payload: post["title"] = payload["title"]
            if "content" in payload: post["content"] = payload["content"]
            return post
    raise HTTPException(status_code=404, detail="No se encontro el post")
    # return {"error": "No se encontro el post"}


@app.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: int):
    for index,post in enumerate(BLOG_POST):
        if post["id"] == post_id:
            BLOG_POST.pop(index)
            return
    raise HTTPException(status_code=404, detail="Post no encontrado")
