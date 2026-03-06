from fastapi import Body, FastAPI, Query, HTTPException

app = FastAPI()

BLOG_POST = [
    {'id': 1, 'title': 'Hola', 'content': 'Primero'},
    {'id': 2, 'title': 'Segundo post', 'content': 'Segundo'},
    {'id': 3, 'title': 'Django vs FasAPI', 'content': 'Aca el contenido'},
]

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
def create_post(post : dict= Body(...)):
    if "title" not in post or "content" not in post:
        return {"error": "Title y content son requeridos"}
    
    if not str(post["title"]).strip():
        # print(f'title: {str(post["title"]).strip()}')
        return {"error": "Title no puede estar vacio"}
    
    new_id = (BLOG_POST[-1]["id"]+1) if BLOG_POST else 1
    # # print(f'New id: {new_id}')
    new_post = {"id": new_id, "title": post["title"], "content": post["content"]}
    # # print(f'New post: {new_post}')
    BLOG_POST.append(new_post)
    
    
    return {"message": "Post creado", "data": BLOG_POST}


@app.put("/posts/{post_id}")
def update_post(post_id: int, data: dict = Body(...)):
    for post in BLOG_POST:
        if post["id"] == post_id:
            if "title" in data: post["title"] = data["title"]
            if "content" in data: post["content"] = data["content"]
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
