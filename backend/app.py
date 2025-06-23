from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
from config import Config
import certifi

app = Flask(__name__) # Initialize Flask app
app.config.from_object(Config)

CORS(app) 
jwt = JWTManager(app) 
try:
    # Check if using MongoDB Atlas (connection string contains 'mongodb+srv')
    if 'mongodb+srv' in app.config['MONGO_URI']:
        # For MongoDB Atlas (cloud)
        from pymongo.server_api import ServerApi
        client = MongoClient(
            app.config['MONGO_URI'], 
            server_api=ServerApi('1'),
            tlsCAFile=certifi.where()
        )
    else:
        # For local MongoDB
        # client = MongoClient(app.config['MONGO_URI'])
        print("No local MongoDB for now")
    
    db = client[app.config['DB_NAME']]
    
    # Test the connection with ping
    client.admin.command('ping')
    print("Connected to MongoDB Atlas successfully!")
    
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")
    db = None

@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to API",
        "status": "running",
        "database": "connected" if db else "disconnected"
    })

if __name__ == '__main__': # 启动 Flask 开发服务器
    app.run(debug=True, host='0.0.0.0', port=5100) # mac 使用5100端口避免 AirPlay Receiver 等接口占用