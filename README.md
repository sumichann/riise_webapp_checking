# notionDBを用いた回答システム
notionDBに回答者の回答内容を反映

## 使用フレームワーク
- notion DB
- fast api 
- S3

## ECRコマンド
```bash
aws ecr get-login-password --region ap-northeast-1 --profile personal | docker login --username AWS --password-stdin 438465133965.dkr.ecr.ap-northeast-1.amazonaws.com
sudo docker build --platform linux/amd64 -t webapp-checking .    
docker tag webapp-checking:latest 438465133965.dkr.ecr.ap-northeast-1.amazonaws.com/webapp-checking:latest
docker push  438465133965.dkr.ecr.ap-northeast-1.amazonaws.com/webapp-checking:latest
