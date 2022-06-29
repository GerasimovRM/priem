from fastapi import FastAPI


app = FastAPI(docs_url="/")


@app.get("/")
