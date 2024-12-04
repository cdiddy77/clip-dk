aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 422882556319.dkr.ecr.us-east-1.amazonaws.com
docker buildx build --platform linux/amd64,linux/arm64 -t labelstudio .
docker tag labelstudio:latest 422882556319.dkr.ecr.us-east-1.amazonaws.com/labelstudio:latest
docker push 422882556319.dkr.ecr.us-east-1.amazonaws.com/labelstudio:latest
