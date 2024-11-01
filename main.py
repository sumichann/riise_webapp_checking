import os
from dotenv import load_dotenv
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import glob
import threading  # threadingモジュールをインポート
from notion_client import Client

# .envファイルを読み込む
load_dotenv()

# Notion APIの設定
notion = Client(auth=os.getenv("NOTION_API_KEY"))
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")



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
    try:
        # NotionDBから項目を取得
        response = notion.databases.query(database_id=DATABASE_ID)
        data = [{
            "Index": item["properties"]["Index"]["number"],
            "Description": item["properties"]["Description"]["rich_text"][0]["text"]["content"],
            "Right Side Composition": item["properties"]["Right Side Composition"]["rich_text"][0]["text"]["content"],
            "Wrong Side Composition": item["properties"]["Wrong Side Composition"]["rich_text"][0]["text"]["content"],
            "washable": item["properties"]["washable"]["rich_text"][0]["text"]["content"]
        } for item in response["results"]]
        return templates.TemplateResponse("index.html", {"request": request, "data": data})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



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
    try:
        # NotionDB内の該当アイテムを取得
        response = notion.databases.query(
            database_id=DATABASE_ID,
            filter={"property": "Item ID", "rich_text": {"equals": anon_item_id}}
        )
        if not response["results"]:
            raise HTTPException(status_code=404, detail="Item not found")

        item = response["results"][0]
        item_data = {
            "Index": item["properties"]["Index"]["number"],
            "Item ID": item["properties"]["Item ID"]["rich_text"][0]["text"]["content"],
            "Description": item["properties"]["Description"]["rich_text"][0]["text"]["content"],
            "Right Side Composition": item["properties"]["Right Side Composition"]["rich_text"][0]["text"]["content"],
            "Wrong Side Composition": item["properties"]["Wrong Side Composition"]["rich_text"][0]["text"]["content"],
            "Washable": item["properties"]["Washable"]["rich_text"][0]["text"]["content"]
        }
        print(item_data)
        return templates.TemplateResponse("item.html", {"request": request, "item": item_data})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_images/{anon_item_id}")
async def get_images(anon_item_id: str):
    # test_photosディレクトリから画像を取得
    image_dir = 'test_photos'
    pattern = os.path.join(image_dir, f'{anon_item_id}_*.jpg')
    image_files = glob.glob(pattern)
    image_urls = [f'/test_photos/{os.path.basename(file)}' for file in image_files]
    return JSONResponse(image_urls)