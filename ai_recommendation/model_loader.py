"""
모델 로더 모듈
저장된 모델과 데이터를 로드하여 서버에서 사용할 수 있도록 제공합니다.
"""

import os
import pickle
import json
import numpy as np
from gensim.models import Word2Vec
from typing import Dict, Any, Optional

class ModelLoader:
    """학습된 모델과 데이터를 로드하는 클래스"""
    
    def __init__(self, model_dir: Optional[str] = None):
        """
        Args:
            model_dir: 모델이 저장된 디렉토리 경로 (None이면 기본값 사용)
        """
        if model_dir is None:
            # 현재 파일 기준으로 models 디렉토리 찾기
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            model_dir = os.path.join(BASE_DIR, "models")
        
        self.model_dir = model_dir
        self.w2v_model: Optional[Word2Vec] = None
        self.color_fabric_model: Optional[Word2Vec] = None
        self.merged_df = None
        self.filtered_df = None
        self.params: Dict[str, Any] = {}
        self._is_loaded = False
    
    def load(self) -> bool:
        """
        저장된 모델과 데이터를 모두 로드합니다.
        
        Returns:
            bool: 로드 성공 여부
        """
        try:
            # 파라미터 로드
            params_path = os.path.join(self.model_dir, "params.json")
            if not os.path.exists(params_path):
                raise FileNotFoundError(f"파라미터 파일을 찾을 수 없습니다: {params_path}")
            
            with open(params_path, 'r', encoding='utf-8') as f:
                self.params = json.load(f)
            
            # Word2Vec 모델 로드
            w2v_model_path = os.path.join(self.model_dir, "w2v_model.model")
            if not os.path.exists(w2v_model_path):
                raise FileNotFoundError(f"Word2Vec 모델 파일을 찾을 수 없습니다: {w2v_model_path}")
            
            self.w2v_model = Word2Vec.load(w2v_model_path)
            
            # Color/Fabric 모델 로드
            color_fabric_model_path = os.path.join(self.model_dir, "color_fabric_model.model")
            if not os.path.exists(color_fabric_model_path):
                raise FileNotFoundError(f"Color/Fabric 모델 파일을 찾을 수 없습니다: {color_fabric_model_path}")
            
            self.color_fabric_model = Word2Vec.load(color_fabric_model_path)
            
            # 병합 데이터 로드
            merged_df_path = os.path.join(self.model_dir, "merged_df.pkl")
            if not os.path.exists(merged_df_path):
                raise FileNotFoundError(f"병합 데이터 파일을 찾을 수 없습니다: {merged_df_path}")
            
            with open(merged_df_path, 'rb') as f:
                self.merged_df = pickle.load(f)
            
            # 필터링 데이터 로드
            filtered_df_path = os.path.join(self.model_dir, "filtered_df.pkl")
            if not os.path.exists(filtered_df_path):
                raise FileNotFoundError(f"필터링 데이터 파일을 찾을 수 없습니다: {filtered_df_path}")
            
            with open(filtered_df_path, 'rb') as f:
                self.filtered_df = pickle.load(f)
            
            self._is_loaded = True
            return True
            
        except Exception as e:
            print(f"❌ 모델 로드 실패: {e}")
            self._is_loaded = False
            return False
    
    def is_loaded(self) -> bool:
        """모델이 로드되었는지 확인"""
        return self._is_loaded
    
    def get_w2v_vector(self, token: str) -> np.ndarray:
        """
        Word2Vec 벡터를 가져옵니다.
        
        Args:
            token: 토큰 문자열
            
        Returns:
            np.ndarray: 벡터 (없으면 zero vector)
        """
        if not self._is_loaded:
            raise RuntimeError("모델이 로드되지 않았습니다. load()를 먼저 호출하세요.")
        
        vector_size = self.params['w2v_vector_size']
        if token in self.w2v_model.wv:
            return self.w2v_model.wv[token]
        else:
            return np.zeros(vector_size)
    
    def get_color_vector(self, color: str) -> np.ndarray:
        """
        색상 벡터를 가져옵니다.
        
        Args:
            color: 색상 문자열
            
        Returns:
            np.ndarray: 벡터 (없으면 zero vector)
        """
        if not self._is_loaded:
            raise RuntimeError("모델이 로드되지 않았습니다. load()를 먼저 호출하세요.")
        
        vector_size = self.params['cf_vector_size']
        if isinstance(color, str) and color.lower() in self.color_fabric_model.wv:
            return self.color_fabric_model.wv[color.lower()]
        else:
            return np.zeros(vector_size)
    
    def get_fabric_vector(self, fabric: str) -> np.ndarray:
        """
        재질 벡터를 가져옵니다.
        
        Args:
            fabric: 재질 문자열
            
        Returns:
            np.ndarray: 벡터 (없으면 zero vector)
        """
        if not self._is_loaded:
            raise RuntimeError("모델이 로드되지 않았습니다. load()를 먼저 호출하세요.")
        
        vector_size = self.params['cf_vector_size']
        if isinstance(fabric, str) and fabric.lower() in self.color_fabric_model.wv:
            return self.color_fabric_model.wv[fabric.lower()]
        else:
            return np.zeros(vector_size)
    
    def sentence_to_vector(self, tokens: list) -> np.ndarray:
        """
        문장(토큰 리스트)을 벡터로 변환합니다.
        
        Args:
            tokens: 토큰 리스트
            
        Returns:
            np.ndarray: 평균 벡터
        """
        if not self._is_loaded:
            raise RuntimeError("모델이 로드되지 않았습니다. load()를 먼저 호출하세요.")
        
        vector_size = self.params['w2v_vector_size']
        vectors = [self.w2v_model.wv[word] for word in tokens if word in self.w2v_model.wv]
        return np.mean(vectors, axis=0) if vectors else np.zeros(vector_size)
    
    def get_params(self) -> Dict[str, Any]:
        """파라미터를 반환합니다."""
        return self.params.copy()
    
    def get_merged_df(self):
        """병합된 데이터프레임을 반환합니다."""
        if not self._is_loaded:
            raise RuntimeError("모델이 로드되지 않았습니다. load()를 먼저 호출하세요.")
        return self.merged_df
    
    def get_filtered_df(self):
        """필터링된 데이터프레임을 반환합니다."""
        if not self._is_loaded:
            raise RuntimeError("모델이 로드되지 않았습니다. load()를 먼저 호출하세요.")
        return self.filtered_df


# 싱글톤 인스턴스 (서버에서 한 번만 로드)
_model_loader_instance: Optional[ModelLoader] = None

def get_model_loader(model_dir: Optional[str] = None) -> ModelLoader:
    """
    싱글톤 패턴으로 ModelLoader 인스턴스를 반환합니다.
    서버 시작 시 한 번만 로드하여 재사용합니다.
    
    Args:
        model_dir: 모델 디렉토리 경로 (None이면 기본값 사용)
        
    Returns:
        ModelLoader: 모델 로더 인스턴스
    """
    global _model_loader_instance
    
    if _model_loader_instance is None:
        _model_loader_instance = ModelLoader(model_dir)
        if not _model_loader_instance.load():
            raise RuntimeError("모델 로드에 실패했습니다.")
    
    return _model_loader_instance

