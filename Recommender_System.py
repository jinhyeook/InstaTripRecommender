from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from konlpy.tag import Okt
from collections import Counter
import pymysql
import re
import numpy as np

vectorizer = CountVectorizer()
keywords_matrix = None

def process_text(input_text):
    okt = Okt()
    nouns = okt.nouns(input_text)
    stop_words = ["은", "는", "이", "가", "을", "를", "에", "에서", "곳", "와", "찍기", "좋은", "찍", "추천"]
    nouns = [word for word in nouns if word not in stop_words]
    return nouns

def get_top_recommendations(user_keywords, places, cosine_sim, top_n=3):
    user_vector = vectorizer.transform([user_keywords])
    sim_scores = cosine_similarity(user_vector, keywords_matrix).flatten()
    sorted_indices = np.argsort(sim_scores)[::-1]
    top_recommendations = [(places[i], sim_scores[i]) for i in sorted_indices[:top_n]]
    return top_recommendations

# (),
# 관강지 데이터(튜플형태로 관광지에 대한 키워드 저장)
def connect_to_database():
    try:
        # MySQL 데이터베이스에 연결
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='your_password',
            database='bigdata'
        )

        return connection

    except Exception as e:
        print(f"데이터베이스 연결 중 오류 발생: {e}")
        return None


def execute_query(query, connection):
    try:
        # SQL 쿼리 실행을 위한 커서 생성
        cursor = connection.cursor()

        # 쿼리 실행
        cursor.execute(query)

        # 모든 행 가져오기
        result = cursor.fetchall()

        # 커서 닫기
        cursor.close()

        return result

    except Exception as e:
        print(f"쿼리 실행 중 오류 발생: {e}")
        return None


def selectPlace(place):
    try:
        # 데이터베이스에 연결
        connection = connect_to_database()

        if not connection:
            return []

        # 특정 장소를 기준으로 place_data 테이블에서 데이터 선택하는 쿼리
        query = f"SELECT place, keyword FROM place_data WHERE region = '{place}'"


        # 쿼리 실행
        result = execute_query(query, connection)

        # 연결 닫기
        connection.close()

        if not result:
            # 특정 장소에 대한 데이터가 없을 경우
            print(f"{place}에 대한 데이터를 찾을 수 없습니다.")
            return []

        # 결과를 원하는 형식으로 변환 (튜플의 리스트)
        places_keywords = [(row[0], row[1]) for row in result]

        return places_keywords

    except Exception as e:
        print(f"{place}에 대한 데이터를 가져오는 동안 오류 발생: {e}")
        return []

def mainAI(place, tag):
    global keywords_matrix  # 전역 범위에서 keywords_matrix를 사용하도록 변경

    keywords = selectPlace(place)
    print(keywords)

    places_keywords = keywords

    # 장소와 키워드를 분리합니다.
    places, keywords = zip(*places_keywords)

    # 키워드를 벡터화합니다.
    keywords_matrix = vectorizer.fit_transform(keywords)

    # 코사인 유사도 행렬을 계산합니다.
    cosine_sim = cosine_similarity(keywords_matrix, keywords_matrix)

    input_sentence = tag

    # 텍스트 전처리 및 키워드 추출
    result_keywords = process_text(input_sentence)

    print("\n키워드:", result_keywords)

    # 키워드 리스트를 합쳐서 하나의 문자열로 만듭니다.
    user_keywords_combined = ' '.join(result_keywords)

    # 추천을 받고 싶은 키워드를 바탕으로 추천을 계산합니다.
    top_recommendations = get_top_recommendations(user_keywords_combined, places, cosine_sim)


    # 추천한 장소의 유사도가 모두 0.00이면 해당 메시지를 출력합니다.
    if all(score == 0.00 for place, score in top_recommendations):
        print("\n입력하신 내용으로 추천할 여행지가 없습니다. 대신 가보기 좋은 다른 장소를 추천해드리겠습니다.")
        print("\n다른 가보기 좋은 여행지:")
        for place, score in top_recommendations:
            print(f"{place} (유사도: {score:.2f})")
    else:
        # 결과를 출력합니다.
        print("\n장소 추천 (Top 3):")
        for place, score in top_recommendations:
            print(f"{place} (유사도: {score:.2f})")

    print("\n장소 리스트:")
    print([place for place, score in top_recommendations])

    pattern = re.compile(r'[^가-힣\s]')
    recommand_region = [pattern.sub('', place) for place, score in top_recommendations]
    regions = '_'.join(recommand_region)
    return regions.strip()