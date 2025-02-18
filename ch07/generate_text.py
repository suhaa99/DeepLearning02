# coding: utf-8
import sys
sys.path.append(r'C:/Users/장수하/OneDrive/문서/GitHub/DeepLearning02/ch07') 
from rnnlm_gen import RnnlmGen
from dataset import ptb


corpus, word_to_id, id_to_word = ptb.load_data('train')
vocab_size = len(word_to_id)
corpus_size = len(corpus)

model = RnnlmGen()
model.load_params(r'C:/Users/장수하/OneDrive/문서/GitHub/DeepLearning02/ch06/Rnnlm.pkl')

# start 문자와 skip 문자 설정
start_word = 'you'
start_id = word_to_id[start_word]
skip_words = ['N', '<unk>', '$']  # N : 숫자로 전처리 되어있음, <unk> : 자주 등장하지 않는 단어
skip_ids = [word_to_id[w] for w in skip_words]
# 문장 생성
word_ids = model.generate(start_id, skip_ids)
txt = ' '.join([id_to_word[i] for i in word_ids])  # 어휘 사이에 스페이스 두기
txt = txt.replace(' <eos>', '.\n')
print(txt)