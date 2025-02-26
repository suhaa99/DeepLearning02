# coding: utf-8
import sys
sys.path.append(r'C:/Users/장수하/OneDrive/문서/GitHub/DeepLearning02')
sys.path.append('..')
from common.np import *  # import numpy as np
from common.layers import Embedding, SigmoidWithLoss
import collections


class EmbeddingDot:
    def __init__(self, W):
        # Wout transpose -> Win.shape
        self.embed = Embedding(W)  
        self.params = self.embed.params
        self.grads = self.embed.grads
        self.cache = None

    def forward(self, h, idx):
        target_W = self.embed.forward(idx)  # idx : target의 인덱스
        # 슬라이싱한 W와 은닉층 행렬 h의 각 행과 내적
        out = np.sum(target_W * h, axis=1)

        # cache : 중간값 저장
        self.cache = (h, target_W)
        return out  # out = score

    def backward(self, dout):
        h, target_W = self.cache
        dout = dout.reshape(dout.shape[0], 1)  # 열벡터로 transpose

        # 은닉층 h와 스칼라 곱
        dtarget_W = dout * h
        self.embed.backward(dtarget_W)
        # Wout과 스칼라 곱
        dh = dout * target_W
        return dh


class UnigramSampler:
    def __init__(self, corpus, power, sample_size):
        self.sample_size = sample_size
        self.vocab_size = None
        self.word_p = None

        counts = collections.Counter()
        for word_id in corpus:
            counts[word_id] += 1
            # counts = count({word_id : 등장횟수}),  ex) {0:1, 1:2, 2:1 ...}

        vocab_size = len(counts)
        self.vocab_size = vocab_size

        self.word_p = np.zeros(vocab_size)
        for i in range(vocab_size):
            self.word_p[i] = counts[i]  # [d1, d2, d3 ...] : 등장횟수

        self.word_p = np.power(self.word_p, power)
        self.word_p /= np.sum(self.word_p)

    def get_negative_sample(self, target):
        batch_size = target.shape[0]

        if not GPU:
            negative_sample = np.zeros((batch_size, self.sample_size), dtype=np.int32)

            for i in range(batch_size):
                p = self.word_p.copy()
                target_idx = target[i]
                # 정답에 해당하는 확률을 0으로 만들어서 샘플링 안뽑히게함
                p[target_idx] = 0  
                p /= p.sum()
                # 확률이 0인 값(정답)은 안뽑힘
                # replace = False : 뽑힌게 또 뽑힐 수 있음
                negative_sample[i, :] = np.random.choice(self.vocab_size, size=self.sample_size, replace=False, p=p)
        else:
            # GPU(cupy）로 계산할 때는 속도를 우선한다.
            # 부정적 예에 타깃이 포함될 수 있다.
            negative_sample = np.random.choice(self.vocab_size, size=(batch_size, self.sample_size),
                                               replace=True, p=self.word_p)

        return negative_sample


class NegativeSamplingLoss:
    def __init__(self, W, corpus, power=0.75, sample_size=5):
        self.sample_size = sample_size
        self.sampler = UnigramSampler(corpus, power, sample_size)
        # sample size + 1 : negative sampling 갯수 + 정답 1개
        self.loss_layers = [SigmoidWithLoss() for _ in range(sample_size + 1)]
        self.embed_dot_layers = [EmbeddingDot(W) for _ in range(sample_size + 1)]

        self.params, self.grads = [], []
        for layer in self.embed_dot_layers:
            self.params += layer.params
            self.grads += layer.grads

    def forward(self, h, target):
        # 미니배치 크기 구함
        batch_size = target.shape[0]
        negative_sample = self.sampler.get_negative_sample(target)

        # 긍정적 예(정답) 순전파
        score = self.embed_dot_layers[0].forward(h, target)
        correct_label = np.ones(batch_size, dtype=np.int32)
        loss = self.loss_layers[0].forward(score, correct_label)

        # 부정적 예 순전파
        negative_label = np.zeros(batch_size, dtype=np.int32)
        for i in range(self.sample_size):
            negative_target = negative_sample[:, i]
            score = self.embed_dot_layers[1 + i].forward(h, negative_target)
            loss += self.loss_layers[1 + i].forward(score, negative_label)  # sum node

        return loss

    def backward(self, dout=1):
        dh = 0
        # zip : col1 = l0(sigmoidwithloss 인스턴스), col2 = l1(embeddingdot 인스턴스)
        for l0, l1 in zip(self.loss_layers, self.embed_dot_layers):
            dscore = l0.backward(dout)
            dh += l1.backward(dscore)

        return dh