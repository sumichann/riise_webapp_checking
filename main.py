import os
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import glob
import threading  # threadingモジュールをインポート



# テンプレートの設定
templates = Jinja2Templates(directory="templates")

app = FastAPI()

# 静的ファイルの設定
app.mount("/test_photos", StaticFiles(directory="test_photos"), name="test_photos")

# ファイルロック用のロックオブジェクト
file_lock = threading.Lock()  # ロックの初期化

class UpdateItem(BaseModel):
    anon_item_id: str
    new_data: dict

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    with open("sample.json", "r", encoding='utf-8') as f:
        data = json.load(f)
    return templates.TemplateResponse("index.html", {"request": request, "data": data})

@app.post("/update_item")
async def update_item(update: UpdateItem):
    try:
        with file_lock:  # ファイルロックを使用
            with open("sample.json", "r+", encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    if item["anon_item_id"] == update.anon_item_id:
                        print("aaaaaaaaaaa")
                        item.update(update.new_data)
                        break
                else:
                    raise HTTPException(status_code=404, detail="Item not found")
                print("aaaa")
                f.seek(0)
                print("a")
                json.dump(data, f, ensure_ascii=False, indent=4)
                f.truncate()
        return {"message": "Item updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/item/{anon_item_id}", response_class=HTMLResponse)
async def show_item(request: Request, anon_item_id: str):
    with open("sample.json", "r") as f:
        data = json.load(f)
    item = next((item for item in data if item["anon_item_id"] == anon_item_id), None)
    return templates.TemplateResponse("item.html", {"request": request, "item": item, "data": data})

@app.get("/get_images/{anon_item_id}")
async def get_images(anon_item_id: str):
    # test_photosディレクトリから画像を取得
    image_dir = 'test_photos'
    pattern = os.path.join(image_dir, f'{anon_item_id}_*.jpg')
    image_files = glob.glob(pattern)
    image_urls = [f'/test_photos/{os.path.basename(file)}' for file in image_files]
    return JSONResponse(image_urls)