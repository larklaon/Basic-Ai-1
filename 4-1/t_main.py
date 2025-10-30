import pandas as pd  # 엑셀과 비슷한 표 형태의 데이터를 다루는 라이브러리
import matplotlib.pyplot as plt  # 그래프를 그리는 라이브러리


# MacOS 한글 폰트 설정 (그래프에서 한글이 깨지지 않도록)
plt.rcParams['font.family'] = 'AppleGothic'  # 애플고딕 폰트 사용
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호가 깨지지 않도록 설정


def print_basic_info(df, name):
    '''데이터프레임 기본 정보를 출력한다.
    
    df: 분석할 데이터프레임 (표 형태의 데이터)
    name: 데이터 이름 (Train, Test, Merged)
    '''
    print(f'\n[{name}] 데이터 정보')
    print(f'총 행 수: {len(df)}')  # len()은 행의 개수를 세는 함수
    print(f'총 열 수: {len(df.columns)}')  # df.columns는 모든 열 이름 목록
    print('\n열별 정보:')
    
    # df.columns의 각 열 이름을 하나씩 꺼내서 처리
    for col in df.columns:
        # notna()는 각 값이 유효한지 확인, sum()으로 개수를 셈
        non_null_count = df[col].notna().sum()
        # nunique()는 중복 제거한 고유값 개수를 세는 메소드
        unique_count = df[col].nunique(dropna=True)
        print(f'- {col}: 유효한 값={non_null_count}, 고유값={unique_count}')


def classify_age_group(age):
    '''나이를 연령대로 분류한다.
    
    age: 나이 숫자 (예: 25, 30, 45)
    반환: '10대', '20대' 등의 문자열
    '''
    # pd.isna()는 값이 NaN(없는 값)인지 확인
    if pd.isna(age):
        return None  # NaN이면 None을 반환
    if age < 20:
        return '10대'
    if age < 30:
        return '20대'
    if age < 40:
        return '30대'
    if age < 50:
        return '40대'
    if age < 60:
        return '50대'
    if age < 70:
        return '60대'
    return '70대 이상'


def convert_boolean_column(series):
    '''불리언 컬럼을 안전하게 0/1로 변환한다.
    
    series: True/False 값을 가진 열
    반환: 0/1로 변환된 열
    '''
    # series.dtype은 데이터 타입을 확인
    if series.dtype == 'object':  # 'object'는 문자열 타입
        # map()은 값을 변환하는 메소드
        # 'True' 문자열 → 1, 'False' 문자열 → 0으로 변환
        result = series.map({'True': 1, 'False': 0, True: 1, False: 0})
    elif series.dtype == 'bool':  # 불리언 타입인 경우
        # astype(int)는 데이터 타입을 정수로 변환 (True→1, False→0)
        result = series.astype(int)
    else:
        result = series
    # fillna(0)은 NaN 값을 0으로 채움
    return result.fillna(0).astype(int)


def prepare_correlation_data(data):
    '''상관계수 계산을 위한 데이터 전처리 후 숫자형 데이터프레임을 반환한다.
    
    상관계수는 숫자끼리만 계산할 수 있으므로 모든 데이터를 숫자로 변환
    '''
    # Transported 값이 있는 행만 필터링 (Train 데이터만 사용)
    # copy()는 원본 데이터를 보호하기 위해 복사본을 만듦
    corr_data = data[data['Transported'].notna()].copy()

    # Transported를 정수(1/0)로 변환
    corr_data['Transported'] = convert_boolean_column(corr_data['Transported'])

    # 불리언 컬럼들을 1/0으로 변환
    # 리스트 컴프리헨션: 조건에 맞는 요소만 모아서 리스트 생성
    boolean_columns = [col for col in ['CryoSleep', 'VIP'] if col in corr_data.columns]
    for col in boolean_columns:
        corr_data[col] = convert_boolean_column(corr_data[col])

    # 범주형 변수(문자열)를 정수로 인코딩
    categorical_columns = [col for col in ['HomePlanet', 'Destination'] if col in corr_data.columns]
    for col in categorical_columns:
        # dropna()는 NaN 제거, unique()는 중복 제거한 고유값 반환
        unique_vals = corr_data[col].dropna().unique()
        # enumerate()는 인덱스(0,1,2...)와 값을 함께 반환
        # 예: ['Earth', 'Mars'] → Earth=0, Mars=1
        mapping = {val: idx for idx, val in enumerate(unique_vals)}
        # map()으로 문자열을 숫자로 변환
        corr_data[col] = corr_data[col].map(mapping)

    # 상관계수 계산에 사용할 숫자형 컬럼 목록
    candidate_columns = [
        'Age', 'RoomService', 'FoodCourt', 'ShoppingMall', 'Spa', 'VRDeck',
        'CryoSleep', 'VIP', 'HomePlanet', 'Destination', 'Transported'
    ]
    # 실제로 데이터에 존재하는 컬럼만 선택
    present_cols = [c for c in candidate_columns if c in corr_data.columns]

    # 결측값(NaN) 처리
    for col in present_cols:
        # 지출 관련 항목은 0원 지출로 간주
        if col in ['RoomService', 'FoodCourt', 'ShoppingMall', 'Spa', 'VRDeck']:
            corr_data[col] = corr_data[col].fillna(0)
        # 나이는 중앙값으로 채움 (median()은 데이터를 정렬했을 때 가운데 값)
        elif col == 'Age':
            corr_data[col] = corr_data[col].fillna(corr_data[col].median())

    # 여전히 NaN이 남아있는 행을 제거
    analysis_data = corr_data[present_cols].dropna()

    return analysis_data


def main():
    # ========== 1단계: CSV 파일 읽기 ==========
    # read_csv()는 CSV 파일을 읽어서 표 형태의 데이터프레임으로 변환
    train_data = pd.read_csv('train.csv')
    test_data = pd.read_csv('test.csv')

    # ========== 2단계: 데이터 구조 확인 ==========
    # 앞에서 정의한 함수를 호출하여 Train, Test 데이터 정보 출력
    print_basic_info(train_data, 'Train')
    print_basic_info(test_data, 'Test')

    # ========== 3단계: 데이터 병합 ==========
    # concat()은 여러 데이터프레임을 위아래로 연결
    # ignore_index=True는 인덱스를 0부터 다시 매김
    merged_data = pd.concat([train_data, test_data], ignore_index=True)
    
    # 병합된 데이터 정보 출력
    print_basic_info(merged_data, 'Merged')
    
    # 병합된 데이터를 CSV 파일로 저장
    # index=False는 인덱스 번호를 저장하지 않음
    # encoding='utf-8-sig'는 한글이 깨지지 않도록 인코딩 설정
    merged_data.to_csv('merged_data.csv', index=False, encoding='utf-8-sig')
    print('\n병합된 데이터를 merged_data.csv 파일로 저장했습니다.')

    # ========== 4단계: 연령대 컬럼 생성 ==========
    # apply()는 각 행에 함수를 적용
    # Age 열의 각 값을 classify_age_group 함수에 넣어서 연령대로 변환
    merged_data['AgeGroup'] = merged_data['Age'].apply(classify_age_group)

    # ========== 5단계: 연령대별 Transported 그래프 ==========
    # Train 데이터만 추출 (Transported 값이 있는 데이터)
    train_only = merged_data[merged_data['Transported'].notna()].copy()
    # AgeGroup에 NaN이 있는 행 제거
    age_df = train_only.dropna(subset=['AgeGroup'])
    
    if not age_df.empty:
        # groupby()는 그룹별로 데이터를 묶음
        # size()는 각 그룹의 개수를 세고
        # unstack()은 데이터를 표 형태로 펼침
        age_counts = age_df.groupby(['AgeGroup', 'Transported']).size().unstack(fill_value=0)

        # 연령대를 순서대로 정렬
        age_order = ['10대', '20대', '30대', '40대', '50대', '60대', '70대 이상']
        # reindex()는 원하는 순서대로 행을 재배열
        age_counts = age_counts.reindex(age_order).fillna(0)
        # 열도 False, True 순서로 정렬하고 정수형으로 변환
        age_counts = age_counts.reindex(columns=[False, True], fill_value=0).astype(int)

        # 열 이름을 한글로 변경 (그래프에서 보기 좋게)
        plot_df = age_counts.rename(columns={False: '전송되지 않음', True: '전송됨'})
        
        # plot()으로 막대 그래프 그리기
        # kind='bar': 막대 그래프
        # figsize=(12, 6): 그래프 크기 (가로 12인치, 세로 6인치)
        # color: 막대 색상 (빨강, 청록색)
        # rot=0: x축 라벨 회전 각도 (0도는 회전 없음)
        ax = plot_df.plot(kind='bar', figsize=(12, 6), color=['#FF6B6B', '#4ECDC4'], rot=0)
        
        # 그래프 꾸미기
        ax.set_title('연령대별 Transported 여부', fontsize=16)  # 제목
        ax.set_xlabel('연령대', fontsize=12)  # x축 라벨
        ax.set_ylabel('인원 수', fontsize=12)  # y축 라벨
        ax.legend(loc='upper right')  # 범례를 오른쪽 위에 배치
        
        # tight_layout()은 그래프 요소들이 겹치지 않도록 자동 조정
        plt.tight_layout()
        # 그래프를 파일로 저장 (dpi=300은 고해상도)
        plt.savefig('age_transported.png', dpi=300)
        # 그래프를 화면에 표시
        plt.show()

        # 연령대별 전송 비율 계산
        print('\n연령대별 전송 비율(%)')
        # sum(axis=1)은 각 행의 합계 계산 (연령대별 총 인원)
        total_by_age = age_counts.sum(axis=1).replace(0, pd.NA)
        # 전송된 사람 수 / 전체 인원 * 100 = 퍼센트
        # round(2)는 소수점 둘째 자리까지 반올림
        age_rate = (age_counts[True] / total_by_age * 100).round(2)
        for age_group, rate in age_rate.items():
            value = 'N/A' if pd.isna(rate) else f'{rate}%'
            print(f'- {age_group}: {value}')
    else:
        print('\n연령 정보가 없어 연령대별 그래프를 생성할 수 없습니다.')

    # ========== 6단계: 상관계수 분석 ==========
    # 앞에서 정의한 함수로 데이터를 전처리
    analysis_data = prepare_correlation_data(merged_data)
    
    print(f'\n상관계수 분석에 사용된 데이터 수: {len(analysis_data)}')
    
    if analysis_data.empty or len(analysis_data) < 2:
        print('\n상관계수 분석을 위한 유효한 숫자 데이터가 충분하지 않습니다.')
        return

    # corr()은 상관계수 행렬을 계산
    # 모든 열 간의 상관관계를 계산하여 표로 만듦 (-1 ~ 1 사이의 값)
    corr_mat = analysis_data.corr()
    # Transported 열만 추출하고, 자기 자신(Transported)은 제거
    transported_corr = corr_mat['Transported'].drop('Transported')

    # 절댓값 기준으로 내림차순 정렬 (큰 값부터)
    # abs()는 절댓값, sort_values()는 정렬
    transported_corr_sorted = transported_corr.reindex(transported_corr.abs().sort_values(ascending=False).index)

    # 상관계수 출력
    print('\nTransported와의 상관계수 (절댓값 기준 내림차순):')
    for feature, value in transported_corr_sorted.items():
        print(f'- {feature}: {value:.4f}')

    # ========== 7단계: 상위 5개 항목 시각화 ==========
    # 상관계수 상위 5개 항목만 추출
    top_idx = list(transported_corr_sorted.index[:5])
    
    if top_idx:
        # 상위 5개의 상관계수 값
        top_vals = [transported_corr[feat] for feat in top_idx]
        # 양수는 초록색, 음수는 빨간색으로 표시
        colors = ['#2E7D32' if v > 0 else '#C62828' for v in top_vals]

        # subplots()로 새로운 그래프 생성
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # barh()는 가로 막대 그래프
        # range(len(top_idx))는 y축 위치 (0, 1, 2, 3, 4)
        ax.barh(range(len(top_idx)), top_vals, color=colors)
        
        # y축에 항목 이름 표시
        ax.set_yticks(range(len(top_idx)))
        ax.set_yticklabels(top_idx)
        
        ax.set_xlabel('상관계수', fontsize=12)
        ax.set_title('Transported와 상관관계 상위 5개 항목', fontsize=14)
        
        # axvline()은 수직선 그리기 (x=0 위치에 양수/음수 구분선)
        ax.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
        
        plt.tight_layout()
        plt.savefig('correlation_top5.png', dpi=300)
        plt.show()

        # 가장 관련성이 높은 항목 출력
        print(f'\n가장 관련성이 높은 항목: {top_idx[0]}')
        print(f'상관계수: {transported_corr[top_idx[0]]:.4f}')
    else:
        print('\n상관계수를 계산할 항목이 없습니다.')


# 파이썬 프로그램의 시작점
# 이 파일이 직접 실행될 때만 main() 함수가 실행됨
if __name__ == '__main__':
    main()
