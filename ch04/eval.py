# coding: utf-8
import sys, os
sys.path.append(r'C:/Users/장수하/OneDrive/문서/GitHub/DeepLearning02/ch04')
sys.path.append('..')
from common.util import most_similar, analogy
import pickle
# 작업 디렉토리를 변경
os.chdir(r"C:/Users/장수하/OneDrive/문서/GitHub/DeepLearning02/ch04")
print("현재 디렉토리:", os.getcwd())  # 변경된 작업 디렉토리 확인

# 상대 경로로 파일 열기
with open("cbow_params.pkl", "rb") as f:
    data = pickle.load(f)

print("파일 로드 성공!")


pkl_file = 'cbow_params.pkl'
# pkl_file = 'skipgram_params.pkl'

with open(pkl_file, 'rb') as f:
    params = pickle.load(f)
    word_vecs = params['word_vecs']
    word_to_id = params['word_to_id']
    id_to_word = params['id_to_word']

# 가장 비슷한(most similar) 단어 뽑기
querys = ['you', 'year', 'car', 'toyota']
for query in querys:
    most_similar(query, word_to_id, id_to_word, word_vecs, top=5)

# 유추(analogy) 작업
print('-'*50)
analogy('king', 'man', 'queen',  word_to_id, id_to_word, word_vecs)
analogy('take', 'took', 'go',  word_to_id, id_to_word, word_vecs)
analogy('car', 'cars', 'child',  word_to_id, id_to_word, word_vecs)
analogy('good', 'better', 'bad',  word_to_id, id_to_word, word_vecs)