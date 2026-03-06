from fastapi import FastAPI, Query

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


