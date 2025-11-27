from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app) # 프론트엔드와 포트가 다르므로 CORS 허용 필수

# DB 연결 함수
def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ.get('DB_HOST', 'postgres-service'),
        database=os.environ.get('DB_NAME', 'boarddb'),
        user=os.environ.get('DB_USER', 'user'),
        password=os.environ.get('DB_PASSWORD', 'password')
    )
    return conn

# 1. 게시글 목록 조회 + 검색 기능 추가
@app.route('/posts', methods=['GET'])
def get_posts():
    # URL에서 '?keyword=검색어' 부분을 가져옴
    keyword = request.args.get('keyword') 
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # 테이블이 없으면 생성
    cur.execute('CREATE TABLE IF NOT EXISTS posts (id SERIAL PRIMARY KEY, title TEXT, content TEXT);')
    conn.commit()
    
    if keyword:
        # 검색어가 있으면 제목이나 내용에 포함된 것만 찾기 (SQL LIKE 문법)
        search_term = f"%{keyword}%"
        cur.execute("SELECT * FROM posts WHERE title LIKE %s OR content LIKE %s ORDER BY id DESC", (search_term, search_term))
    else:
        # 검색어가 없으면 전체 조회
        cur.execute("SELECT * FROM posts ORDER BY id DESC")
        
    posts = cur.fetchall()
    cur.close()
    conn.close()
    
    post_list = [{'id': p[0], 'title': p[1], 'content': p[2]} for p in posts]
    return jsonify(post_list)


# 2. 게시글 작성 (CREATE)
@app.route('/posts', methods=['POST'])
def create_post():
    new_post = request.get_json()
    title = new_post['title']
    content = new_post['content']
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO posts (title, content) VALUES (%s, %s)', (title, content))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'message': 'Created'}), 201

# 3. 게시글 삭제 (DELETE)
@app.route('/posts/<int:id>', methods=['DELETE'])
def delete_post(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM posts WHERE id = %s', (id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'message': 'Deleted'}), 200

# backend/app.py 에 이 부분이 있는지 꼭 확인하세요!
@app.route('/posts/<int:id>', methods=['PUT'])
def update_post(id):
    data = request.get_json()
    new_title = data['title']
    new_content = data['content']

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE posts SET title = %s, content = %s WHERE id = %s', (new_title, new_content, id))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'message': 'Updated'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
