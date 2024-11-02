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
import requests


# .envファイルを読み込む
load_dotenv()

# Notion APIの設定
notion_api_key = os.getenv("NOTION_API_KEY")
notion = Client(auth=notion_api_key)
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
headers = {
    "Authorization": f"Bearer {notion_api_key}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

class UpdateProperties(BaseModel):
    index: int
    new_property_1: str
    new_property_2: str
    new_property_3: str


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
        all_data = []
        next_cursor = None

        while True:
            response = notion.databases.query(
                database_id=DATABASE_ID,
                start_cursor=next_cursor
            )
            data = [{
                "Index": item["properties"]["Index"]["number"],
                "Item ID": item["properties"]["Item ID"]["rich_text"][0]["text"]["content"],
                "Description": item["properties"]["Description"]["rich_text"][0]["text"]["content"],
                "Right Side Composition": json.dumps(json.loads(item["properties"]["Right Side Composition"]["rich_text"][0]["text"]["content"].encode().decode('unicode_escape')), ensure_ascii=False),  # JSON文字列に変換
                "Wrong Side Composition": json.dumps(json.loads(item["properties"]["Wrong Side Composition"]["rich_text"][0]["text"]["content"].encode().decode('unicode_escape')), ensure_ascii=False),  # JSON文字列に変換
                "Washable": item["properties"]["Washable"]["rich_text"][0]["text"]["content"]
            } for item in response["results"]]

            all_data.extend(data)

            if not response.get("has_more"):
                break
            next_cursor = response.get("next_cursor")

        return templates.TemplateResponse("index.html", {"request": request, "data": all_data})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/update_properties")
def update_properties(data: UpdateProperties):
    # NotionのページIDを取得
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    response = requests.post(url, headers=headers, json={"filter": {"property": "Index", "number": {"equals": data.index}}})
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to retrieve Notion page.")
    
    result = response.json()["results"]
    if not result:
        raise HTTPException(status_code=404, detail="Index not found in NotionDB.")
    
    page_id = result[0]["id"]
    
    # プロパティを更新
    update_url = f"https://api.notion.com/v1/pages/{page_id}"
    payload = {
        "properties": {
            "Composition Check": {"rich_text": [{"text": {"content": data.new_property_1}}]},
            "Size Check": {"rich_text": [{"text": {"content": data.new_property_2}}]},
            "Wash Check": {"rich_text": [{"text": {"content": data.new_property_3}}]}
        }
    }
    update_response = requests.patch(update_url, headers=headers, json=payload)
    if update_response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to update Notion page.")
    
    return {"message": "Properties updated successfully"}

@app.get("/item/{index}", response_class=HTMLResponse)
async def show_item(request: Request, index: str):
    try:
        # NotionDB内の該当アイテムを取得
        response = notion.databases.query(
            database_id=DATABASE_ID,
            filter={"property": "Index", "number": {"equals": int(index)}}
        )
        if not response["results"]:
            raise HTTPException(status_code=404, detail="Item not found")

        item = response["results"][0]
        item_data = {
            "Index": item["properties"]["Index"]["number"],
            "Item ID": item["properties"]["Item ID"]["rich_text"][0]["text"]["content"],
            "Description": item["properties"]["Description"]["rich_text"][0]["text"]["content"],
            "Right Side Composition": json.dumps(json.loads(item["properties"]["Right Side Composition"]["rich_text"][0]["text"]["content"].encode().decode('unicode_escape')), ensure_ascii=False),  # JSON文字列に変換
            "Wrong Side Composition": json.dumps(json.loads(item["properties"]["Wrong Side Composition"]["rich_text"][0]["text"]["content"].encode().decode('unicode_escape')), ensure_ascii=False),  # JSON文字列に変換
            "Washable": item["properties"]["Washable"]["rich_text"][0]["text"]["content"]
        }
        print(item_data)
        #取り出したitemのindexを取得
        # index_this_item = item["properties"]["Index"]["number"]
        
        # #そのindexの両隣のitemも取得
        # if (index_this_item != 2499):
        #     response_next = notion.databases.query(
        #         database_id=DATABASE_ID,
        #         filter={"property": "Index", "number": {"equals": index_this_item + 1}}
        #     )
        #     if not response_next["results"]:
        #         raise HTTPException(status_code=404, detail="Item not found")
        #     item_next = response_next["results"][0]
        #     item_data_next = {
        #     "Index": item_next["properties"]["Index"]["number"],
        #     "Item ID": item_next["properties"]["Item ID"]["rich_text"][0]["text"]["content"],
        #     "Description": item_next["properties"]["Description"]["rich_text"][0]["text"]["content"],
        #     "Right Side Composition": json.dumps(json.loads(item_next["properties"]["Right Side Composition"]["rich_text"][0]["text"]["content"].encode().decode('unicode_escape')), ensure_ascii=False),  # JSON文字列に変換
        #     "Wrong Side Composition": json.dumps(json.loads(item_next["properties"]["Wrong Side Composition"]["rich_text"][0]["text"]["content"].encode().decode('unicode_escape')), ensure_ascii=False),  # JSON文字列に変換
        #     "Washable": item_next["properties"]["Washable"]["rich_text"][0]["text"]["content"]
        #     }
        #     if(index_this_item == 0):
        #         item_data_back = 0
        
        # if(index_this_item != 0):
        #     response_back = notion.databases.query(
        #         database_id=DATABASE_ID,
        #         filter={"property": "Index", "number": {"equals": index_this_item - 1}}
        #     )
        #     if not response_back["results"]:
        #         raise HTTPException(status_code=404, detail="Item not found")
        #     item_back = response_back["results"][0]
        #     item_data_back = {
        #         "Index": item_back["properties"]["Index"]["number"],
        #         "Item ID": item_back["properties"]["Item ID"]["rich_text"][0]["text"]["content"],
        #         "Description": item_back["properties"]["Description"]["rich_text"][0]["text"]["content"],
        #         "Right Side Composition": json.dumps(json.loads(item_back["properties"]["Right Side Composition"]["rich_text"][0]["text"]["content"].encode().decode('unicode_escape')), ensure_ascii=False),  # JSON文字列に変換
        #         "Wrong Side Composition": json.dumps(json.loads(item_back["properties"]["Wrong Side Composition"]["rich_text"][0]["text"]["content"].encode().decode('unicode_escape')), ensure_ascii=False),  # JSON文字列に変換
        #         "Washable": item_back["properties"]["Washable"]["rich_text"][0]["text"]["content"]
        #     }
        #     if(index_this_item == 2499):
        #         item_data_next = 0
            

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