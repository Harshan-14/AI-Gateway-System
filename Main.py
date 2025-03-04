import uuid
from fastapi import FastAPI,HTTPException
import sqlite3
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from pathlib import Path


app=FastAPI()

def initdb():
    connection=sqlite3.connect("database.db")
    cursor=connection.cursor()
    query="""create table if not exists models(
            provider txt,
            model text not null,
            prompt text)"""
    cursor.execute(query)
    connection.commit()
    connection.close()

initdb()

#populating the database
def populate():
    connection=sqlite3.connect("database.db")   
    query1="insert into models values('openai','gpt-3.5','Processed your prompt with advanced language understanding.')"
    connection.execute(query1)
    query2="insert into models values('anthropic','claude-v1','Your prompt has been interpreted with ethical AI principles.')"
    connection.execute(query2)
    query3="insert into models values('meta','opt-13b','potential benifits of AI')"
    connection.execute(query3)
    connection.commit()

@app.get("/models")
def get_items():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    query = "SELECT provider, model FROM models"
    cursor.execute(query)
    models = [{"provider": row[0], "model": row[1]} for row in cursor.fetchall()]
    conn.close()
    return models

class Crequest(BaseModel):
    provider : str
    model : str
    prompt : str

class Cresponse(BaseModel):
    provider : str
    model : str
    response : str

def openai():
    return "OpenAI, the worlds premier AI"
def anthropic():
    return "anthropic, Your prompt has been interpreted with ethical AI principles."
def meta():
    return "The world revolves around us"


@app.post("/v1/chat/completions")
def find_and_fetch(creq: Crequest):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()


    query = "SELECT provider, model FROM models WHERE provider = ? AND model = ?"
    cursor.execute(query, (creq.provider, creq.model))
    result = cursor.fetchone()

    conn.close()

    if not result:
        raise HTTPException(status_code=404, detail="Invalid provider or model")

    # Route to the correct stub function
    if creq.provider.lower() == "openai":
        response_text = openai()
    elif creq.provider.lower() == "anthropic":
        response_text = anthropic()
    elif creq.provider.lower() == "meta":
        response_text = meta()
    else:
        raise HTTPException(status_code=400, detail="Data Unavailable")

    return Cresponse(provider=creq.provider, model=creq.model, response=response_text)


def createtab_regex():
    connection = sqlite3.connect('regex.db')
    cursor = connection.cursor()
    
    query = """CREATE TABLE IF NOT EXISTS regex_table (
                  regex TEXT,
                  model TEXT,
                  redirectmod TEXT
               )"""
    
    cursor.execute(query)
    connection.commit()
    connection.close()

createtab_regex()

def regis_populate():
    connection=sqlite3.connect("regex.db")   
    query1="insert into regex_table values('credit card','openai','meta')"
    connection.execute(query1)
    query2="insert into regex_table values('Debit card','anthropic','openai')"
    connection.execute(query2)
    connection.commit()
    connection.close()

@app.get("/regextabview")
def get_all_regex():
    connection = sqlite3.connect("regex.db")
    cursor = connection.cursor()
    query = "SELECT * FROM regex_table"
    cursor.execute(query)
    data = [{"regex": row[0], "model": row[1], "redirectmod": row[2]} for row in cursor.fetchall()]
    connection.close()
    return data

class Crequest_reg(BaseModel):
    text : str

class Cresponse_reg(BaseModel):
    redirection : str

@app.post('/redirection')
def redirection_model(creq: Crequest_reg):
    connection = sqlite3.connect("regex.db")
    cursor = connection.cursor()

    query = "SELECT regex, redirectmod FROM regex_table"
    cursor.execute(query)
    regex_entries = cursor.fetchall()

    connection.close()

    # Check if input text matches any regex pattern
    for regex_pattern, redirectmod in regex_entries:
        if regex_pattern.lower() in creq.text.lower():  
            return Cresponse_reg(redirection=redirectmod)

    return Cresponse_reg(redirection="cannot be redirected. use the current model")



#admin model
class RegexRule(BaseModel):
    regex: str
    model: str
    redirectmod: str

# get and display all the rules
@app.get("/admin_portal/regex_rules")
def get_all_regex_rules():
    connection = sqlite3.connect("regex.db")
    cursor = connection.cursor()
    query = "SELECT * FROM regex_table"
    cursor.execute(query)
    data = [{"regex": row[0], "model": row[1], "redirectmod": row[2]} for row in cursor.fetchall()]
    connection.close()
    return data

# append a new rule
@app.post("/admin_portal/add_regex")
def add_regex_rule(rule: RegexRule):
    connection = sqlite3.connect("regex.db")
    cursor = connection.cursor()
    
    query = "INSERT INTO regex_table (regex, model, redirectmod) VALUES (?, ?, ?)"
    cursor.execute(query, (rule.regex, rule.model, rule.redirectmod))
    
    connection.commit()
    connection.close()
    
    return {"info": "Regex rule added successfully"} 

# update an already existing rule
@app.put("/admin_portal/update_regex/{regex}")
def update_regex_rule(regex: str, rule: RegexRule):
    connection = sqlite3.connect("regex.db")
    cursor = connection.cursor()
    
    query = "UPDATE regex_table SET model = ?, redirectmod = ? WHERE regex = ?"
    cursor.execute(query, (rule.model, rule.redirectmod, regex))
    
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Rule not found") 

    connection.commit()
    connection.close()
    
    return {"info": "Regex rule updated successfully"}

# Delete a regex rule
@app.delete("/admin_portal/delete_regex/{regex}")
def delete_regex_rule(regex: str):
    connection = sqlite3.connect("regex.db")
    cursor = connection.cursor()
    
    query = "DELETE FROM regex_table WHERE regex = ?"
    cursor.execute(query, (regex,))
    
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Rule not found")  # ✅ Proper error handling

    connection.commit()
    connection.close()
    
    return {"info": "Regex rule deleted successfully"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    upload_dir=Path('uploads')
    upload_dir.mkdir(exist_ok=True)
    filename = upload_dir / file.filename
    with filename.open("wb") as f:
        f.write(await file.read())
    return {"filename": file.filename}

@app.get('/fileupload', response_class=HTMLResponse)
def file_upload():
    templates=Jinja2Templates('templates')
    return templates.TemplateResponse("index.html", {"request": {}})


def create_file_routing_table():
    connection = sqlite3.connect("file_routing.db")
    cursor = connection.cursor()
    
    query = """CREATE TABLE IF NOT EXISTS file_upload_routes (
                  file_type TEXT PRIMARY KEY,
                  provider TEXT,
                  model TEXT
               )"""
    
    cursor.execute(query)
    connection.commit()
    connection.close()

create_file_routing_table()  
def populate_file_routing():
    connection = sqlite3.connect("file_routing.db")   
    query1 = "INSERT OR IGNORE INTO file_upload_routes VALUES ('pdf', 'anthropic', 'claude-v1')"
    connection.execute(query1)
    query2 = "INSERT OR IGNORE INTO file_upload_routes VALUES ('jpg', 'openai', 'dall-e')"
    connection.execute(query2)
    query3 = "INSERT OR IGNORE INTO file_upload_routes VALUES ('txt', 'meta', 'opt-13b')"
    connection.execute(query3)
    connection.commit()
    connection.close()

populate_file_routing()


class FileRouteRule(BaseModel):
    file_type: str
    provider: str
    model: str

@app.post("/admin_portal/add_file_route")
def add_file_route(rule: FileRouteRule):
    connection = sqlite3.connect("file_routing.db")
    cursor = connection.cursor()
    
    query = "INSERT OR REPLACE INTO file_upload_routes (file_type, provider, model) VALUES (?, ?, ?)"
    cursor.execute(query, (rule.file_type.lower(), rule.provider, rule.model))
    
    connection.commit()
    connection.close()
    return {"info": "File upload route added successfully"}

@app.get("/admin_portal/file_routes")
def get_file_routes():
    connection = sqlite3.connect("file_routing.db")
    cursor = connection.cursor()
    query = "SELECT * FROM file_upload_routes"
    cursor.execute(query)
    data = [{"file_type": row[0], "provider": row[1], "model": row[2]} for row in cursor.fetchall()]
    connection.close()
    return data

@app.post("/upload")
def upload_file(file: UploadFile = File(...)):
    file_extension = file.filename.split(".")[-1].lower()

    connection = sqlite3.connect("file_routing.db")
    cursor = connection.cursor()
    
    query = "SELECT provider, model FROM file_upload_routes WHERE file_type = ?"
    cursor.execute(query, (file_extension,))
    result = cursor.fetchone()
    
    connection.close()

    if not result:
        raise HTTPException(status_code=404, detail="No processing route found for this file type.")

    provider, model = result
    response_id = f"{provider}_file_response_{uuid.uuid4().hex[:6]}"

    return {
        "provider": provider,
        "model": model,
        "response": f"{provider.capitalize()}: File processed with secure file analysis. Response ID: {response_id}"
    } 

