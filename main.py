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
import boto3


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
    new_property: str


# テンプレートの設定
templates = Jinja2Templates(directory="templates")

app = FastAPI()


class UpdateItem(BaseModel):
    anon_item_id: str
    new_data: dict
    
@app.get("/health")
def health_check():
    # アプリケーションが正常稼働していることを示すために200 OKを返す
    return JSONResponse(status_code=200, content={"status": "ok"})


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # try:
    #     all_data = []
    #     next_cursor = None

    #     while True:
    #         response = notion.databases.query(
    #             database_id=DATABASE_ID,
    #             start_cursor=next_cursor
    #         )
    #         data = [{
    #             "Index": item["properties"]["Index"]["number"],
    #             "Item ID": item["properties"]["Item ID"]["rich_text"][0]["text"]["content"],
    #             "Description": item["properties"]["Description"]["rich_text"][0]["text"]["content"],
    #             "Right Side Composition": json.dumps(json.loads(item["properties"]["Right Side Composition"]["rich_text"][0]["text"]["content"].encode().decode('unicode_escape')), ensure_ascii=False),  # JSON文字列に変換
    #             "Wrong Side Composition": json.dumps(json.loads(item["properties"]["Wrong Side Composition"]["rich_text"][0]["text"]["content"].encode().decode('unicode_escape')), ensure_ascii=False),  # JSON文字列に変換
    #             "Washable": item["properties"]["Washable"]["rich_text"][0]["text"]["content"]
    #         } for item in response["results"]]

    #         all_data.extend(data)

    #         if not response.get("has_more"):
    #             break
    #         next_cursor = response.get("next_cursor")

    return templates.TemplateResponse("index.html", {"request": request})


'''使用回数のupdate'''
@app.post("/uses/update_properties")
def uses_update_properties(data: UpdateProperties):
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
            "Uses Check": {"rich_text": [{"text": {"content": data.new_property}}]}
        }
    }
    update_response = requests.patch(update_url, headers=headers, json=payload)
    if update_response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to update Notion page.")
    
    return {"message": "Properties updated successfully"}

'''サイズのupdate'''
@app.post("/size/update_properties")
def size_update_properties(data: UpdateProperties):
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
            "Size Check": {"rich_text": [{"text": {"content": data.new_property}}]}
        }
    }
    update_response = requests.patch(update_url, headers=headers, json=payload)
    if update_response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to update Notion page.")
    
    return {"message": "Properties updated successfully"}

'''成分のupdate'''
@app.post("/composition/update_properties")
def composition_update_properties(data: UpdateProperties):
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
            "Composition Check": {"rich_text": [{"text": {"content": data.new_property}}]}
        }
    }
    update_response = requests.patch(update_url, headers=headers, json=payload)
    if update_response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to update Notion page.")
    
    return {"message": "Properties updated successfully"}

'''洗濯表示のupdate'''
@app.post("/wash/update_properties")
def composition_update_properties(data: UpdateProperties):
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
            "Wash Check": {"rich_text": [{"text": {"content": data.new_property}}]}
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
        try:
            number_of_uses = item["properties"]["Number of Uses"]["rich_text"][0]["text"]["content"]
        except (IndexError, KeyError):
            number_of_uses = "currrently under estimation"
        item_data = {
            "Index": item["properties"]["Index"]["number"],
            "Item ID": item["properties"]["Item ID"]["rich_text"][0]["text"]["content"],
            "Description": item["properties"]["Description"]["rich_text"][0]["text"]["content"],
            "Size GPT": item["properties"]["Size GPT"]["rich_text"][0]["text"]["content"],
            "Right Side Composition": json.dumps(json.loads(item["properties"]["Right Side Composition"]["rich_text"][0]["text"]["content"].encode().decode('unicode_escape')), ensure_ascii=False),  # JSON文字列に変換
            "Wrong Side Composition": json.dumps(json.loads(item["properties"]["Wrong Side Composition"]["rich_text"][0]["text"]["content"].encode().decode('unicode_escape')), ensure_ascii=False),  # JSON文字列に変換
            "Washable": item["properties"]["Washable"]["rich_text"][0]["text"]["content"],
            "Number of Uses": number_of_uses,
            "Evidence by GPT": item["properties"]["Evidence by GPT"]["rich_text"][0]["text"]["content"],
        }
        print(item_data)
        return templates.TemplateResponse("item.html", {"request": request, "item": item_data})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @app.get("/get_images/{anon_item_id}")
# async def get_images(anon_item_id: str):
#     # test_photosディレクトリから画像を取得
#     image_dir = 'test_photos'
#     pattern = os.path.join(image_dir, f'{anon_item_id}_*.jpg')
#     image_files = glob.glob(pattern)
#     image_urls = [f'/test_photos/{os.path.basename(file)}' for file in image_files]
#     return JSONResponse(image_urls)


'''ここから項目ごとのエンドポイント'''

'''使用回数'''
@app.get("/uses/item/{index}", response_class=HTMLResponse)
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
        try:
            number_of_uses = item["properties"]["Number of Uses"]["rich_text"][0]["text"]["content"]
        except (IndexError, KeyError):
            number_of_uses = "currrently under estimation"
        item_data = {
            "Index": item["properties"]["Index"]["number"],
            "Item ID": item["properties"]["Item ID"]["rich_text"][0]["text"]["content"],
            "Description": item["properties"]["Description"]["rich_text"][0]["text"]["content"],
            "Number of Uses": number_of_uses,
            "Evidence by GPT": item["properties"]["Evidence by GPT"]["rich_text"][0]["text"]["content"],
        }
        return templates.TemplateResponse("item_uses.html", {"request": request, "item": item_data})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


'''サイズ'''
@app.get("/size/item/{index}", response_class=HTMLResponse)
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
            "Size GPT": item["properties"]["Size GPT"]["rich_text"][0]["text"]["content"],
        }
        return templates.TemplateResponse("item_size.html", {"request": request, "item": item_data})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

'''成分'''
@app.get("/composition/item/{index}", response_class=HTMLResponse)
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
        }
        return templates.TemplateResponse("item_comp.html", {"request": request, "item": item_data})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
'''洗濯'''
@app.get("/wash/item/{index}", response_class=HTMLResponse)
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
            "Washable": item["properties"]["Washable"]["rich_text"][0]["text"]["content"],
        }
        return templates.TemplateResponse("item_wash.html", {"request": request, "item": item_data})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
     

@app.get("/get_images/{anon_item_id}")
async def get_images(anon_item_id: str):
    session = boto3.Session(
        
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_DEFAULT_REGION')
)
    # S3クライアントを作成
    s3 = session.client('s3')
    bucket_name = 'dev-kusahata-2'  # ここにS3バケット名を指定
    prefix = f'test_photos/{anon_item_id}_'  # anon_item_idに基づくプレフィックス

    # S3からファイルをリスト
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    if 'Contents' not in response:
        return JSONResponse([])

    # ファイルのURLを生成
    image_urls = [f'https://{bucket_name}.s3.ap-northeast-1.amazonaws.com/{item["Key"]}' for item in response['Contents']]
    return JSONResponse(image_urls)


#uvicorn main:app --host 0.0.0.0 --port 8877 --reload 