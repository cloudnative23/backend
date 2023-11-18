# 後端
## 前置
1. 按照這個[網址](https://www.learncodewithmike.com/2020/05/django-postgresql.html)PostgreSQL。
*    不用新增Server Group和Server，直接用pgAdmin預設的就好
*    直接右鍵Databases，Create Database，名稱輸入uber_db之後按Save

<img width="435" alt="upload_310c63f6a4ef0a05e6bf6cb27780addc" src="https://github.com/cloudnative23/backend/assets/69982559/bfd080ce-4311-4e43-9bb5-1ea6af42d256">
<img width="698" alt="upload_269224d0d2eb3eb087f84ee9ffeb8660" src="https://github.com/cloudnative23/backend/assets/69982559/5433dd41-6107-4147-9021-3a5ae72a439f">


2. 使PostgreSQL能用python操作
```
pip3 install psycopg2
```
3. 安裝Django
```
python3 -m pip install Django
```
## 建立Django
1. 建立專案(資料夾會自動建立)
```
django-admin startproject uber_project
cd uber_project
```
2. 建立應用
```
python3 manage.py startapp uber_app
```
3. 在 uber_project/settings.py 中，找到 DATABASES 設定，設定成如下：
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  #PostgreSQL
        'NAME': 'uber_db',  #資料庫名稱
        'USER': 'postgres',  #資料庫帳號(預設就是postgres)
        'PASSWORD': 'csie504',  #資料庫密碼(安裝過程postgre中輸入的密碼)
        'HOST': 'localhost',  #Server(伺服器)位址
        'PORT': '5432'  #PostgreSQL Port號(預設就是5432)
    }
}
```
4. 在 uber_app/models.py 中建立資料庫(長度關係，直接參考檔案)
5. 在 uber_project/settings.py 中，找到 INSTALLED_APPS 設定，新增應用程式(最下面那一行)
```
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'uber_app',
]
```
6. 回到project dir紀錄db變動並將Django創立的資料庫相關移到PostgreSQL
```
python3 manage.py makemigrations
python3 manage.py migrate
```
7. 若要登入後台，先創立帳號，否則直接到第八步
```
python3 manage.py createsuperuser
Username (leave blank to use 'shenghsing'): uber
Email address: uber@gmail.com
Password: 
Password (again): 
```
8. 啟動伺服器
```
python3 manage.py runserver
```
9. 輸入下列網址
```
http://127.0.0.1:8000/
```
看到以下畫面代表成功
<img width="1004" alt="upload_8228465598a1ce37d2e6066b2f5d3755" src="https://github.com/cloudnative23/backend/assets/69982559/e58c308a-27ea-4192-8d90-878d42551702">

11. 若要進後台，改輸入為下列網址
```
http://127.0.0.1:8000/admin
```
輸入第七步設定的資料可看到
<img width="952" alt="upload_c1fd65952ade5aa95e875a40dc160eb5" src="https://github.com/cloudnative23/backend/assets/69982559/44645e5a-9888-4395-84d8-afb17eea8aa2">

