# build docker image
gcloud builds submit --tag us-central1-docker.pkg.dev/clip-dk/label-studio/label-studio
# gcloud secrets create labelstudio-svcacct --data-file ungitable/clip-dk-labelstudio-svcacct.json
gcloud run deploy label-studio \
    --image us-central1-docker.pkg.dev/clip-dk/label-studio/label-studio \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --port 8080 \
    --set-env-vars \
USE_ENFORCE_CSRF_CHECKS=false,\
LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED=true,\
GOOGLE_CLOUD_STORAGE_BUCKET_NAME=clip-dk-label-studio-stoage,\
GOOGLE_APPLICATION_CREDENTIALS=projects/clip-dk/secrets/labelstudio-svcacct/versions/latest
