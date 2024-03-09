## début de monorépo pour saas music player / recommandation

manque le .env 
```
MILVUS_URI=
MILVUS_TOKEN=
SHARED_SECRET_KEY= 
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
REGION=
```
et le dataset 

## pour l'instant

- l'api tourne toute seule dans un conteneur.
Elle permet de lire le contenu du dataset (plus tard du S3) et de query Milvus

- la webapp flask tourne en local et contacte l'api.

- js est banni (pour l'instant)

### model trouvé sur https://essentia.upf.edu/models.html