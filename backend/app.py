from flask import Flask # 创建Flask应用
from flask_cors import CORS # 处理跨域资源共享
from flask_jwt_extended import JWTManager # 管理JWT认证
from pymongo import MongoClient # 连接MongoDB数据库
from datetime import timedelta # 置时间间隔
import os
import certifi 
from dotenv import load_dotenv  
load_dotenv() # 读取 .env 文件并把变量添加到 os.environ

# Import Flask routes for Blueprint 
from routes.auth import auth_bp 
# from routes.profiles import profiles_bp
# from routes.preferences import preferences_bp
# from routes.matches import matches_bp
# from routes.chats import chats_bp

def create_app(): # 创建Flask
    app = Flask(__name__) # 初始化Flask 
    
    # Configuration: JWT
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)

    # Configuration: MongoDB
    use_local = os.environ.get('USE_LOCAL_DB', 'false').lower() in ('1', 'true', 'yes')
    if use_local:
        mongo_uri = os.environ.get('LOCAL_MONGO_URI')
        if not mongo_uri: 
            raise RuntimeError("LOCAL_MONGO_URI not being set up, plz check .env")
    else:
        mongo_uri = os.environ.get('MONGO_URI')
        if not mongo_uri: 
            raise RuntimeError("MONGO_URI not being set up, plz check .env")
    app.config['MONGO_URI'] = mongo_uri

    # Initialize extensions: CORS, JWT 
    CORS(app, origins=['http://localhost:*', 'http://127.0.0.1:*'])
    jwt = JWTManager(app)
    
    # Database connection
    if mongo_uri.startswith('mongodb+srv://'):
        from pymongo.server_api import ServerApi
        client = MongoClient(
            mongo_uri,
            server_api=ServerApi('1'),
            tlsCAFile=certifi.where()
        )
    else:
        client = MongoClient(mongo_uri)
    # Use default database from URI path or MONGO_DB_NAME
    try:
        app.db = client.get_default_database()
    except Exception:
        app.db = client[os.environ.get('MONGO_DB_NAME')]
    # Print current DB location and ping test
    print(f"Using {'local' if use_local else 'remote'} MongoDB: {mongo_uri}")
    try:
        app.db.command('ping')
        print("===== MongoDB ping successful =====")
    except Exception as e:
        print(f"===== MongoDB ping failed ===== \n {e}")

    # -- Register Blueprints -- Each blueprint defines its own routes under the given URL prefix
    app.register_blueprint(auth_bp, url_prefix='/auth')
    # app.register_blueprint(profiles_bp, url_prefix='/profiles')
    # app.register_blueprint(preferences_bp, url_prefix='/preferences')
    # app.register_blueprint(matches_bp, url_prefix='/matches')
    # app.register_blueprint(chats_bp, url_prefix='/chats')
    return app

if __name__ == '__main__':
    app = create_app() 
    app.run(debug=True, host='0.0.0.0', port=5100) # 启动服务器，开启debug，接受所有IP链接，指定端口为5100[apple tv 占用5000, thx apple ：) ]